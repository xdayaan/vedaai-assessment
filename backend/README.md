# VedaAI Assessment Extraction & Answer Mapping Backend

A high-precision, lightweight FastAPI backend for automated AI assessment processing. It ingests arbitrary Question Papers and Student Handwritten Answer Sheets (in PDF or image format), extracts questions, extracts handwritten answers, deterministically maps answers to questions, detects spatial bounding boxes for UI highlight overlays, and handles complex edge cases (sub-parts, multi-page answers, out-of-order responses, unanswered questions, duplicate answers, and unmatched scribbles).

---

## Architecture Overview

```text
Next.js Frontend
       │
       ▼
FastAPI Backend (app/main.py)
       │
       ├── 1. PDF / Image Rendering (pdf_service.py)
       │      └─ Renders high-res page images with PyMuPDF/Pillow
       │
       ├── 2. Coordinate-Preserving OCR (ocr_service.py)
       │      └─ Digital vector extraction + OCR with line/word bounding boxes
       │
       ├── 3. Question Extraction & Hierarchy (question_extractor.py)
       │      └─ Normalizes numbering, separates sub-parts 11(a) & 11(b), preserves printed order
       │
       ├── 4. Answer Extraction & Region Detection (answer_extractor.py)
       │      └─ Handles out-of-order responses, multi-page spans, computes line-level & region bboxes
       │
       ├── 5. Deterministic Mapping Engine (mapping_service.py)
       │      └─ Exact -> Normalized -> Contextual -> Semantic matching
       │      └─ Detects unanswered questions, unmatched scribbles, duplicate attempts
       │
       └── 6. Result Generation & File Serving (processing_service.py)
              └─ Saves result.json & serves rendered page images
```

---

## WSL Setup & Execution Guide

All backend execution is performed inside **WSL (Windows Subsystem for Linux)**.

### 1. Prerequisites
Ensure Python 3 is installed in your WSL distribution:
```bash
python3 --version
```

### 2. Navigate to Backend Directory
```bash
cd /mnt/d/code/Personal/veda-ai-v1/backend
```
*(Adjust the mount path according to your Windows drive location)*

### 3. Create & Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the FastAPI Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Alternative ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 6. Run Automated Test Suite
```bash
pytest tests/ -v
```

### 7. Run Standalone CLI Processing Script
Run the processing pipeline directly on any Question Paper and Answer Sheet without starting the web servers:
```bash
python scripts/process.py \
    /path/to/question_paper.pdf \
    /path/to/student_answer_sheet.pdf \
    --output result.json
```

---

## API Documentation

### 1. Upload Assessment Files
`POST /api/assessments`
* **Content-Type**: `multipart/form-data`
* **Form Fields**:
  * `question_paper`: File (`.pdf`, `.png`, `.jpg`, `.jpeg`, `.webp`)
  * `answer_sheet`: File (`.pdf`, `.png`, `.jpg`, `.jpeg`, `.webp`)
* **Response (201 Created)**:
```json
{
  "assessment_id": "asm_9f83a12b01",
  "status": "uploaded"
}
```

---

### 2. Trigger Background Processing Pipeline
`POST /api/assessments/{assessment_id}/process`
* Initiates the multi-stage extraction pipeline using non-blocking FastAPI `BackgroundTasks`.
* **Response (200 OK)**:
```json
{
  "assessment_id": "asm_9f83a12b01",
  "status": "processing"
}
```

---

### 3. Poll Processing Stage & Progress
`GET /api/assessments/{assessment_id}/status`
* **Response (200 OK)**:
```json
{
  "assessment_id": "asm_9f83a12b01",
  "status": "processing",
  "stage": "answer_extraction",
  "progress": 70,
  "error": null
}
```
**Pipeline Stages**:
1. `uploaded` (0%)
2. `rendering` (15%) — Document pages rendered into high-resolution PNGs
3. `question_extraction` (40%) — Questions, subparts, marks extracted in printed sequence
4. `answer_extraction` (70%) — Handwritten answers, line bounding boxes, multi-page spans detected
5. `mapping` (90%) — Deterministic matching, edge case handling, rubric & score calculation
6. `completed` (100%) — `result.json` written and ready for consumption

---

### 4. Retrieve Complete Assessment Result
`GET /api/assessments/{assessment_id}`
* **Response (200 OK)**:
```json
{
  "id": "asm_9f83a12b01",
  "title": "Extracted Assessment & Answer Mapping",
  "totalMaxMarks": 47.0,
  "totalScoredMarks": 38.0,
  "percentage": 80.8,
  "pages": [
    {
      "pageNumber": 1,
      "image": "/api/assessments/asm_9f83a12b01/pages/as/page_1.png",
      "width": 1200,
      "height": 1600,
      "label": "Page 1 of 4"
    }
  ],
  "questions": [
    {
      "id": "q11a",
      "questionNumber": 11,
      "subPart": "a",
      "displayNumber": "11(a)",
      "text": "A diagram shows two potted plants – Plant A in bright light, Plant B in dim light.",
      "maxMarks": 2.0,
      "scoredMarks": 2.0,
      "aiSuggestedMarks": 2.0,
      "status": "correct",
      "pageNumber": 4,
      "spansPages": [4],
      "boundingBox": {
        "x": 4.5,
        "y": 4.5,
        "width": 91.0,
        "height": 25.5,
        "page": 4,
        "unit": "percentage"
      },
      "studentAnswerText": "Plant B is exhibiting etiolation because in dim light...",
      "aiFeedback": "Accurately identified etiolation phenomenon."
    }
  ],
  "unansweredQuestions": ["4"],
  "unmatchedAnswers": [
    {
      "id": "unmatched-1",
      "pageNumber": 4,
      "boundingBox": { "x": 65.0, "y": 92.0, "width": 30.0, "height": 6.0 },
      "snippet": "Rough note: Photosystem II absorption peak = 680 nm",
      "note": "Extra student scribble not matching any question prompt."
    }
  ]
}
```

---

### 5. Rendered Page Image Stream
`GET /api/assessments/{assessment_id}/pages/{page_type}/{page_filename}`
* `page_type`: `qp` (Question Paper) or `as` (Answer Sheet)
* Serves the rendered PNG page image for live frontend visualization.

---

## Edge Case Handling

1. **Sub-parts Preservation (`11(a)`, `11(b)`)**: Sub-questions are never merged into parent Q11; they remain independent entities with their own individual marks, feedback, and coordinates.
2. **Out-of-Order Answers**: Student can answer in any order (e.g. Q5, Q1, Q10, Q3, Q11(b), Q2); answers are mapped accurately to the question paper's printed order.
3. **Multi-Page Spans**: Answers spanning across page boundaries (e.g. starting on Page 2 and finishing on Page 3) contain bounding boxes and page references for all touched pages.
4. **Unanswered Questions**: Missing answers are marked `status: "unanswered"`, score 0, and included in `unansweredQuestions`.
5. **Unmatched / Extraneous Answers**: Answers with non-existent numbers (e.g. Q99) or unassigned scribbles are captured in `unmatchedAnswers` without failing the pipeline.
6. **Duplicate Answers**: When multiple attempts exist for the same question, all attempts are preserved and flagged.

---

## OCR & Handwriting Limitations

* **Heavily Cursive / Low-Contrast Handwriting**: If OCR confidence drops on faint pencil or irregular handwriting, the system preserves line-level region coordinates and uses fallback contextual matching.
* **Diagrams and Visual Math**: Complex scientific diagrams (e.g. nephrons, electrical circuits) are segmented as contiguous bounding box regions, allowing visual inspection on the frontend viewer even when text transcription is sparse.
* **Rotated / Skewed Scans**: Clean, upright scans provide the highest accuracy; slight skews are handled by baseline line clustering tolerances.

# VedaAI: Assessment Extraction and Answer Mapping

An automated document understanding system that processes printed question papers and handwritten student answer sheets. The system extracts individual questions, transcribes handwritten responses, and deterministically maps answers to questions with spatial bounding box highlights for grading and review.

---

## The Problem

Grading handwritten student answer sheets against printed question papers is a time-consuming and manual process. Real-world student submissions present several technical challenges:

1. Students frequently write answers out of order (e.g., answering Question 3 before Question 1).
2. Multi-part questions (like 11(a) and 11(b)) need to be extracted and evaluated as distinct question entries.
3. Long answers often span multiple physical pages.
4. Students skip questions (unanswered questions) or include rough work and unrelated notes (unmatched scribbles).
5. Scanned handwritten documents vary significantly in legibility, lighting, and alignment.

VedaAI solves these challenges by combining computer vision, deep learning OCR, and multimodal language models to automate the entire extraction, segmentation, and mapping pipeline.

---

## Development Journey

Building this system required balancing design precision on the frontend with robust, resilient document processing on the backend. Here is how the project was architected and built:

### 1. Design Implementation via Figma MCP
To ensure the user interface strictly followed the design specification rather than generic templates, the Figma Model Context Protocol (MCP) toolchain was used during development. 

By pulling layout metrics, typography hierarchies, exact color tokens, and frame hierarchies directly from the Figma canvas into the Next.js component tree, the interface mirrors the intended product experience. This includes the dual-upload hub, the interactive question cards, the score pills, and the continuous document viewer.

### 2. Deep Multimodal Understanding with Google Gemini Vision
Handwritten answer sheets are notoriously difficult for traditional template-matching algorithms. To solve this, the backend integrates Google Gemini Vision (using Gemini 3.6 Flash).

Gemini processes the rendered question paper and student answer sheet pages simultaneously. It performs full handwriting transcription, identifies question numbers and sub-parts, calculates normalized bounding box coordinates for each answer region, assesses answers against marking rubrics, and flags unmatched student scribbles.

### 3. Resilient Offline Fallback (RapidOCR & PyMuPDF)
To ensure the backend never fails even when internet connectivity is intermittent or cloud API quotas are reached, a local fallback pipeline was built using:
- **PyMuPDF**: For high-resolution document page rendering and digital vector text coordinate extraction.
- **RapidOCR (ONNX Runtime)**: A self-contained deep-learning OCR model running in pure Python without requiring external system packages (like Tesseract binaries).
- **Deterministic Mapping Engine**: A priority-based matching engine that resolves question labels using exact string matches, normalized patterns, and spatial layout clustering.

### 4. Dual-Mode User Experience
To give evaluators immediate access to the system without requiring them to prepare PDF files or wait for processing, the application was built with two distinct modes:

- **Mode 1: Instant Frontend Demo Mode**: By clicking "Try with Sample Assignment", the frontend loads a pre-structured sample assessment directly into client state. Evaluators can immediately test the continuous document viewer, zoom controls, bounding box highlights, question filtering, and rubric feedback without any backend dependency.
- **Mode 2: Live Backend Mode**: When users upload their own Question Paper and Answer Sheet files (PDF or images), the frontend transmits them to the FastAPI backend, tracks live progress through an animated multi-stage checklist, and renders the live extracted bounding boxes and grades.

---

## Key Features

- **Printed Sequence Preservation**: Questions are extracted in their exact document order.
- **Sub-Part Isolation**: Questions like 11(a) and 11(b) are segmented as independent items with individual marks and rubrics.
- **Multi-Page Spanning**: Answers extending across page boundaries (e.g., Pages 2 and 3) are tracked with bounding boxes rendered on each relevant page.
- **Edge-Case Handling**: Automatically categorizes skipped questions as unanswered and isolates extra rough notes as unmatched student scribbles.
- **Continuous Scroll Viewer**: All answer sheet pages are stacked in a smooth, continuous vertical document feed. Selecting any question card automatically scrolls the viewer to center on that question's highlighted region.
- **Score Customization**: Graders can interactively adjust marks awarded to each question, which dynamically recalculates total scores and performance percentages.

---

## System Architecture

```
veda-ai-v1/
├── frontend/                     # Next.js 14 Web Application
│   ├── app/                      # App router, page views, and layout
│   ├── components/               # UI components (UploadScreen, MappingScreen, AnswerSheetViewer)
│   ├── data/                     # Sample offline assessment dataset
│   └── utils/                    # API client and status polling helpers
│
├── backend/                      # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py               # Application entry point and CORS configuration
│   │   ├── api/                  # REST endpoints (/assessments, /process, /status)
│   │   ├── services/             # Core processing engines
│   │   │   ├── ai_service.py     # Gemini Vision multimodal extraction
│   │   │   ├── pdf_service.py    # PyMuPDF rendering and vector text extraction
│   │   │   ├── ocr_service.py    # RapidOCR and PyTesseract spatial OCR
│   │   │   ├── question_extractor.py # Regex question parser and subpart splitter
│   │   │   ├── answer_extractor.py   # Answer segmenter and bounding box builder
│   │   │   ├── mapping_service.py    # Deterministic matching and edge-case engine
│   │   │   └── processing_service.py # Pipeline coordinator and state management
│   │   ├── models/               # Pydantic schemas (Question, Answer, Assessment, BoundingBox)
│   │   └── core/                 # Settings and environment configuration
│   ├── scripts/                  # Standalone CLI tools and test data generators
│   └── tests/                    # Automated pytest suite (12 unit and integration tests)
```

---

## Local Setup and Running

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+ (WSL recommended on Windows)

---

### Backend Setup (FastAPI)

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Copy `.env.example` to `.env` and configure your settings:
   ```bash
   cp .env.example .env
   ```
   Add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. Start the backend development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The backend API will be available at `http://localhost:8000` (API documentation at `http://localhost:8000/docs`).

6. Run automated tests:
   ```bash
   pytest tests/ -v
   ```

---

### Frontend Setup (Next.js)

1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

4. Start the frontend development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.

---

### Running via Standalone CLI Script

You can also run the extraction and answer mapping pipeline directly from the command line without starting a web server:

```bash
cd backend
source .venv/bin/activate
python scripts/process.py path/to/question_paper.pdf path/to/answer_sheet.pdf --output result.json
```

---

## Deployment Summary

- **Frontend**: Deployed on Vercel with automatic rewrites and client-side demo fallbacks.
- **Backend**: Deployed on Render as a persistent Python Web Service running Uvicorn.

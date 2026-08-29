import os
import base64
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx

from app.models.schemas import (
    Assessment,
    QuestionResult,
    BoundingBox,
    UnmatchedAnswer,
    PageInfo,
)

logger = logging.getLogger("veda_ai.ai_service")

GEMINI_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
]


class AIService:
    @staticmethod
    def encode_image_base64(image_path: Path) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @classmethod
    def extract_with_gemini_vision(
        cls,
        assessment_id: str,
        qp_image_paths: List[Path],
        as_image_paths: List[Path],
        pages_info: List[PageInfo],
        api_key: str,
        exam_name: str = "question_paper.pdf",
        answer_sheet_name: str = "student_answer_sheet.pdf"
    ) -> Optional[Assessment]:
        """
        Calls Gemini Multimodal Vision API with question paper and answer sheet page images.
        Extracts questions, transcribed handwriting, line-level bounding box percentage coordinates,
        evaluates marks against rubric, and detects unanswered and unmatched scribbles.
        """
        if not api_key:
            return None

        prompt = f"""
You are an expert AI Assessment Examiner and Document Vision Engine.
You are given:
1. Question Paper page images ({len(qp_image_paths)} pages)
2. Student's Handwritten Answer Sheet page images ({len(as_image_paths)} pages)

Your task:
1. Extract ALL questions from the Question Paper in their EXACT printed sequence.
2. Preserve question numbering and treat sub-parts like 11(a) and 11(b) as separate question entries.
3. For each question, locate the student's handwritten answer on the Answer Sheet.
4. Detect the exact bounding box region on the answer sheet in 0-100 percentage coordinates:
   - x: percentage from left edge (0 to 100)
   - y: percentage from top edge (0 to 100)
   - width: percentage width (0 to 100)
   - height: percentage height (0 to 100)
   - pageNumber: 1-indexed page where this answer appears
5. If an answer spans multiple pages, specify all touched pages in `spansPages` (e.g. [2, 3]).
6. Transcribe the student's handwritten response accurately in `studentAnswerText`.
7. Evaluate the student's answer:
   - maxMarks: number (default 2 or 5 depending on question)
   - scoredMarks: number (marks awarded based on accuracy)
   - aiSuggestedMarks: number
   - status: "correct" if full marks, "partial" if partial marks, "unanswered" if skipped/missing
   - aiFeedback: constructive 1-2 sentence grading feedback
8. If a question has NO answer on the student answer sheet:
   - mark status as "unanswered", scoredMarks: 0, pageNumber: null, boundingBox: null, studentAnswerText: null
9. If the student has extra scribbles, rough notes, or answers for non-existent questions (e.g., Q99):
   - record them in `unmatchedAnswers` with their pageNumber and boundingBox.

Return ONLY valid JSON matching this exact structure:
{{
  "title": "Extracted Assessment & Answer Mapping",
  "subject": "Exam Assessment",
  "className": "Class 10",
  "totalMaxMarks": 47.0,
  "totalScoredMarks": 38.0,
  "percentage": 80.8,
  "questions": [
    {{
      "id": "q1",
      "questionNumber": 1,
      "subPart": null,
      "displayNumber": "1",
      "text": "Question text...",
      "maxMarks": 2.0,
      "scoredMarks": 2.0,
      "aiSuggestedMarks": 2.0,
      "status": "correct",
      "pageNumber": 1,
      "spansPages": [1],
      "boundingBox": {{ "x": 4.5, "y": 4.5, "width": 91.0, "height": 12.0 }},
      "studentAnswerText": "Transcribed student handwriting...",
      "aiFeedback": "Accurate response.",
      "rubric": {{ "concept": "Key Concept", "keywords": ["keyword1"] }}
    }}
  ],
  "unansweredQuestions": ["4"],
  "unmatchedAnswers": [
    {{
      "id": "unmatched-1",
      "pageNumber": 2,
      "boundingBox": {{ "x": 60.0, "y": 80.0, "width": 35.0, "height": 8.0 }},
      "snippet": "Rough note text...",
      "note": "Extra student scribble not matching any question prompt."
    }}
  ]
}}
"""

        parts: List[Dict[str, Any]] = [{"text": prompt}]

        # Add Question Paper images
        for i, qp_p in enumerate(qp_image_paths, start=1):
            parts.append({"text": f"--- QUESTION PAPER PAGE {i} ---"})
            parts.append({
                "inlineData": {
                    "mimeType": "image/png",
                    "data": cls.encode_image_base64(qp_p)
                }
            })

        # Add Answer Sheet images
        for i, as_p in enumerate(as_image_paths, start=1):
            parts.append({"text": f"--- STUDENT ANSWER SHEET PAGE {i} ---"})
            parts.append({
                "inlineData": {
                    "mimeType": "image/png",
                    "data": cls.encode_image_base64(as_p)
                }
            })

        req_body = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1,
            }
        }

        for model_name in GEMINI_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            try:
                logger.info(f"Calling Gemini Vision API ({model_name})...")
                with httpx.Client(timeout=90.0) as client:
                    resp = client.post(url, json=req_body)

                if resp.status_code != 200:
                    logger.warning(f"Gemini API ({model_name}) returned status {resp.status_code}: {resp.text[:200]}")
                    continue

                res_json = resp.json()
                candidates = res_json.get("candidates", [])
                if not candidates:
                    continue

                content_parts = candidates[0].get("content", {}).get("parts", [])
                if not content_parts:
                    continue

                raw_text = content_parts[0].get("text", "").strip()
                if raw_text.startswith("```"):
                    raw_text = raw_text.strip("`")
                    if raw_text.startswith("json"):
                        raw_text = raw_text[4:].strip()

                parsed = json.loads(raw_text)

                # Convert questions to QuestionResult instances
                question_results: List[QuestionResult] = []
                for q in parsed.get("questions", []):
                    bbox_data = q.get("boundingBox")
                    bbox = BoundingBox(
                        x=float(bbox_data.get("x", 5.0)),
                        y=float(bbox_data.get("y", 5.0)),
                        width=float(bbox_data.get("width", 90.0)),
                        height=float(bbox_data.get("height", 15.0)),
                        page=q.get("pageNumber") or 1,
                        unit="percentage"
                    ) if bbox_data else None

                    bboxes_list = [bbox] if bbox else []

                    question_results.append(
                        QuestionResult(
                            id=str(q.get("id") or f"q{q.get('questionNumber', 1)}"),
                            questionNumber=int(q.get("questionNumber", 1)),
                            subPart=q.get("subPart"),
                            displayNumber=str(q.get("displayNumber") or q.get("questionNumber", 1)),
                            text=str(q.get("text", "")),
                            maxMarks=float(q.get("maxMarks", 2.0)),
                            scoredMarks=float(q.get("scoredMarks", 0.0)),
                            aiSuggestedMarks=float(q.get("aiSuggestedMarks", q.get("scoredMarks", 0.0))),
                            status=str(q.get("status", "correct")),
                            pageNumber=q.get("pageNumber"),
                            spansPages=q.get("spansPages", [q.get("pageNumber")] if q.get("pageNumber") else []),
                            boundingBox=bbox,
                            bboxes=bboxes_list,
                            studentAnswerText=q.get("studentAnswerText"),
                            aiFeedback=q.get("aiFeedback"),
                            rubric=q.get("rubric", {}),
                        )
                    )

                # Unmatched answers
                unmatched_list: List[UnmatchedAnswer] = []
                for u in parsed.get("unmatchedAnswers", []):
                    u_bbox_data = u.get("boundingBox", {})
                    u_bbox = BoundingBox(
                        x=float(u_bbox_data.get("x", 50.0)),
                        y=float(u_bbox_data.get("y", 80.0)),
                        width=float(u_bbox_data.get("width", 30.0)),
                        height=float(u_bbox_data.get("height", 6.0)),
                        page=int(u.get("pageNumber", 1)),
                        unit="percentage"
                    )
                    unmatched_list.append(
                        UnmatchedAnswer(
                            id=str(u.get("id") or f"unmatched-{len(unmatched_list)+1}"),
                            pageNumber=int(u.get("pageNumber", 1)),
                            boundingBox=u_bbox,
                            snippet=str(u.get("snippet", "")),
                            note=str(u.get("note", "Extra student scribble."))
                        )
                    )

                # Calculate marks
                total_max = sum(q.maxMarks for q in question_results)
                total_scored = sum(q.scoredMarks for q in question_results)
                pct = round((total_scored / total_max * 100.0), 1) if total_max > 0 else 0.0

                unanswered = [q.displayNumber for q in question_results if q.status == "unanswered"]

                assessment = Assessment(
                    id=assessment_id,
                    title=str(parsed.get("title", "Extracted Assessment & Answer Mapping")),
                    subject=str(parsed.get("subject", "Exam Assessment")),
                    className=str(parsed.get("className", "Standard Evaluation")),
                    examName=exam_name,
                    answerSheetName=answer_sheet_name,
                    questionPaperPages=len(qp_image_paths),
                    answerSheetPages=len(as_image_paths),
                    totalMaxMarks=round(total_max, 1),
                    totalScoredMarks=round(total_scored, 1),
                    percentage=pct,
                    pages=pages_info,
                    questions=question_results,
                    unansweredQuestions=unanswered,
                    unmatchedAnswers=unmatched_list,
                )

                logger.info(f"Gemini Vision successfully extracted {len(question_results)} questions with high-precision bounding boxes!")
                return assessment

            except Exception as e:
                logger.warning(f"Gemini extraction attempt failed with model {model_name}: {e}")

        return None

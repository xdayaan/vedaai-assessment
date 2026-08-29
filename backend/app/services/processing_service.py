import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List

from app.core.config import settings
from app.models.schemas import (
    Assessment,
    ProcessingStatus,
    OCRLine,
    OCRWord,
    PageInfo,
)
from app.services.pdf_service import PDFService
from app.services.ocr_service import OCRService
from app.services.question_extractor import QuestionExtractor
from app.services.answer_extractor import AnswerExtractor
from app.services.mapping_service import MappingService
from app.services.ai_service import AIService

logger = logging.getLogger("veda_ai.processing_service")

# In-memory stores
_STATUS_STORE: Dict[str, ProcessingStatus] = {}
_RESULT_STORE: Dict[str, Assessment] = {}


class ProcessingService:
    @classmethod
    def get_status(cls, assessment_id: str) -> ProcessingStatus:
        if assessment_id in _STATUS_STORE:
            return _STATUS_STORE[assessment_id]

        # Check if result.json already exists on disk
        result_file = settings.TEMP_DIR / assessment_id / "result.json"
        if result_file.exists():
            return ProcessingStatus(
                assessment_id=assessment_id,
                status="completed",
                stage="completed",
                progress=100
            )

        # Check if directory exists
        assessment_dir = settings.TEMP_DIR / assessment_id
        if assessment_dir.exists():
            return ProcessingStatus(
                assessment_id=assessment_id,
                status="uploaded",
                stage="uploaded",
                progress=0
            )

        return ProcessingStatus(
            assessment_id=assessment_id,
            status="not_found",
            stage="not_found",
            progress=0,
            error=f"Assessment {assessment_id} not found."
        )

    @classmethod
    def set_status(
        cls,
        assessment_id: str,
        status: str,
        stage: str,
        progress: int,
        error: Optional[str] = None
    ) -> None:
        _STATUS_STORE[assessment_id] = ProcessingStatus(
            assessment_id=assessment_id,
            status=status,
            stage=stage,
            progress=progress,
            error=error
        )
        logger.info(f"[{assessment_id}] Status -> {status} | Stage -> {stage} | {progress}%")

    @classmethod
    def get_assessment(cls, assessment_id: str) -> Optional[Assessment]:
        if assessment_id in _RESULT_STORE:
            return _RESULT_STORE[assessment_id]

        result_file = settings.TEMP_DIR / assessment_id / "result.json"
        if result_file.exists():
            try:
                with open(result_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                assessment = Assessment(**data)
                _RESULT_STORE[assessment_id] = assessment
                return assessment
            except Exception as e:
                logger.error(f"Failed to load cached result.json for {assessment_id}: {e}")

        return None

    @classmethod
    def process_assessment(cls, assessment_id: str) -> Assessment:
        """
        Executes the full assessment extraction and mapping pipeline:
        1. Render PDF / images to page image cache
        2. Extract questions and coordinates from question paper
        3. Extract answers, multi-page spans, and bounding boxes from answer sheet
        4. Deterministically map answers to questions & handle edge cases
        5. Save result.json and complete
        """
        logger.info(f"Starting processing pipeline for assessment: {assessment_id}")
        assessment_dir = settings.TEMP_DIR / assessment_id

        if not assessment_dir.exists():
            cls.set_status(assessment_id, "failed", "failed", 0, "Assessment folder does not exist.")
            raise FileNotFoundError(f"Assessment directory {assessment_dir} not found.")

        try:
            # Locate uploaded files
            qp_files = list(assessment_dir.glob("question_paper.*"))
            as_files = list(assessment_dir.glob("answer_sheet.*"))

            if not qp_files or not as_files:
                err = "Missing question_paper or answer_sheet file in assessment directory."
                cls.set_status(assessment_id, "failed", "failed", 0, err)
                raise FileNotFoundError(err)

            qp_path = qp_files[0]
            as_path = as_files[0]

            # Stage 1: Rendering (15%)
            cls.set_status(assessment_id, "processing", "rendering", 15)
            qp_pages_dir = assessment_dir / "question_pages"
            as_pages_dir = assessment_dir / "answer_pages"

            qp_page_prefix = f"{settings.API_PREFIX}/assessments/{assessment_id}/pages/qp"
            as_page_prefix = f"{settings.API_PREFIX}/assessments/{assessment_id}/pages/as"

            qp_pages_info = PDFService.render_document_pages(
                qp_path, qp_pages_dir, dpi=settings.PDF_DPI, api_page_prefix=qp_page_prefix
            )
            as_pages_info = PDFService.render_document_pages(
                as_path, as_pages_dir, dpi=settings.PDF_DPI, api_page_prefix=as_page_prefix
            )

            # Option A: Gemini Multimodal Vision API (if API key is configured)
            if settings.GEMINI_API_KEY:
                try:
                    cls.set_status(assessment_id, "processing", "question_extraction", 35)
                    qp_image_paths = sorted(
                        list(qp_pages_dir.glob("page_*.png")),
                        key=lambda p: int(p.stem.split("_")[-1])
                    )
                    as_image_paths = sorted(
                        list(as_pages_dir.glob("page_*.png")),
                        key=lambda p: int(p.stem.split("_")[-1])
                    )

                    cls.set_status(assessment_id, "processing", "answer_extraction", 65)
                    ai_assessment = AIService.extract_with_gemini_vision(
                        assessment_id=assessment_id,
                        qp_image_paths=qp_image_paths,
                        as_image_paths=as_image_paths,
                        pages_info=as_pages_info,
                        api_key=settings.GEMINI_API_KEY,
                        exam_name=qp_path.name,
                        answer_sheet_name=as_path.name,
                    )

                    if ai_assessment and ai_assessment.questions:
                        cls.set_status(assessment_id, "processing", "mapping", 90)
                        result_file = assessment_dir / "result.json"
                        with open(result_file, "w", encoding="utf-8") as f:
                            json.dump(ai_assessment.model_dump(), f, indent=2)

                        _RESULT_STORE[assessment_id] = ai_assessment
                        cls.set_status(assessment_id, "completed", "completed", 100)
                        logger.info(f"Gemini Vision successfully processed and saved assessment {assessment_id}")
                        return ai_assessment

                except Exception as e:
                    logger.warning(f"Gemini Vision pipeline failed, falling back to local OCR pipeline: {e}")

            # Option B: Local OCR & Deterministic Pipeline
            # Stage 2: Question Extraction (40%)
            cls.set_status(assessment_id, "processing", "question_extraction", 40)
            
            # Extract digital words if PDF or run OCR
            qp_words_by_page = PDFService.extract_digital_text_words(qp_path, dpi=settings.PDF_DPI)
            qp_lines_by_page: Dict[int, List[OCRLine]] = {}

            for p_info in qp_pages_info:
                p_num = p_info.pageNumber
                words = qp_words_by_page.get(p_num, [])
                if not words:
                    # Fallback to OCR on rendered image
                    page_img_path = qp_pages_dir / f"page_{p_num}.png"
                    words = OCRService.ocr_image_file(page_img_path, page_num=p_num)

                lines = OCRService.cluster_words_into_lines(words, page_num=p_num)
                qp_lines_by_page[p_num] = lines

            questions = QuestionExtractor.extract_questions_from_lines(qp_lines_by_page, qp_pages_info)
            if not questions:
                logger.warning(f"No questions detected in {qp_path}. Creating fallback single question.")
                # Fallback: Create at least one question so UI doesn't crash on blank or image-only documents
                questions = [
                    QuestionExtractor._build_question(
                        {
                            "id": "q1",
                            "number": 1,
                            "sub_part": None,
                            "display_number": "1",
                            "text_parts": ["Extracted Assessment Question 1"],
                            "page": 1,
                            "lines": [],
                        },
                        qp_pages_info[0].width if qp_pages_info else 1200,
                        qp_pages_info[0].height if qp_pages_info else 1600,
                    )
                ]

            # Stage 3: Answer Extraction (70%)
            cls.set_status(assessment_id, "processing", "answer_extraction", 70)
            
            as_words_by_page = PDFService.extract_digital_text_words(as_path, dpi=settings.PDF_DPI)
            as_lines_by_page: Dict[int, List[OCRLine]] = {}

            for p_info in as_pages_info:
                p_num = p_info.pageNumber
                words = as_words_by_page.get(p_num, [])
                if not words:
                    page_img_path = as_pages_dir / f"page_{p_num}.png"
                    words = OCRService.ocr_image_file(page_img_path, page_num=p_num)

                lines = OCRService.cluster_words_into_lines(words, page_num=p_num)
                as_lines_by_page[p_num] = lines

            answers, unmatched_scribbles = AnswerExtractor.extract_answers_from_lines(
                as_lines_by_page, as_pages_info
            )

            # Stage 4: Answer Mapping (90%)
            cls.set_status(assessment_id, "processing", "mapping", 90)
            
            assessment = MappingService.map_assessment(
                assessment_id=assessment_id,
                questions=questions,
                answers=answers,
                existing_unmatched=unmatched_scribbles,
                pages_info=as_pages_info,
                exam_name=qp_path.name,
                answer_sheet_name=as_path.name,
            )

            # Stage 5: Completed (100%)
            result_file = assessment_dir / "result.json"
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(assessment.model_dump(), f, indent=2)

            _RESULT_STORE[assessment_id] = assessment
            cls.set_status(assessment_id, "completed", "completed", 100)
            logger.info(f"Successfully finished assessment processing for: {assessment_id}")

            return assessment

        except Exception as e:
            logger.error(f"Processing failed for assessment {assessment_id}: {e}", exc_info=True)
            cls.set_status(assessment_id, "failed", "failed", 0, str(e))
            raise

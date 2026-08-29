import os
import uuid
import shutil
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse

from app.core.config import settings
from app.models.schemas import (
    UploadResponse,
    ProcessResponse,
    ProcessingStatus,
    Assessment,
)
from app.services.processing_service import ProcessingService

logger = logging.getLogger("veda_ai.api.assessments")

router = APIRouter(prefix="/assessments", tags=["Assessments"])


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_assessment_files(
    question_paper: UploadFile = File(..., description="Question paper file (PDF or Image)"),
    answer_sheet: UploadFile = File(..., description="Student handwritten answer sheet file (PDF or Image)"),
):
    """
    Accepts question paper and answer sheet files (PDF or PNG/JPG/JPEG/WEBP).
    Stores them in a unique temporary directory and initializes processing state.
    """
    try:
        assessment_id = f"asm_{uuid.uuid4().hex[:10]}"
        assessment_dir = settings.TEMP_DIR / assessment_id
        os.makedirs(assessment_dir, exist_ok=True)

        # Get file extensions
        qp_ext = Path(question_paper.filename or "question_paper.pdf").suffix or ".pdf"
        as_ext = Path(answer_sheet.filename or "answer_sheet.pdf").suffix or ".pdf"

        qp_target = assessment_dir / f"question_paper{qp_ext}"
        as_target = assessment_dir / f"answer_sheet{as_ext}"

        # Write uploaded files to disk
        with open(qp_target, "wb") as f_qp:
            shutil.copyfileobj(question_paper.file, f_qp)

        with open(as_target, "wb") as f_as:
            shutil.copyfileobj(answer_sheet.file, f_as)

        # Initialize status
        ProcessingService.set_status(assessment_id, "uploaded", "uploaded", 0)

        logger.info(f"Uploaded assessment {assessment_id} (QP: {question_paper.filename}, AS: {answer_sheet.filename})")

        return UploadResponse(assessment_id=assessment_id, status="uploaded")

    except Exception as e:
        logger.error(f"Failed to upload assessment files: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload assessment: {str(e)}"
        )


@router.post("/{assessment_id}/process", response_model=ProcessResponse)
async def start_assessment_processing(
    assessment_id: str,
    background_tasks: BackgroundTasks
):
    """
    Starts the assessment extraction and mapping pipeline asynchronously.
    Returns immediately with status 'processing'.
    """
    assessment_dir = settings.TEMP_DIR / assessment_id
    if not assessment_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found."
        )

    # Set initial processing status
    ProcessingService.set_status(assessment_id, "processing", "rendering", 5)

    # Add background processing task without Celery/Redis
    background_tasks.add_task(ProcessingService.process_assessment, assessment_id)

    return ProcessResponse(assessment_id=assessment_id, status="processing")


@router.get("/{assessment_id}/status", response_model=ProcessingStatus)
async def get_assessment_status(assessment_id: str):
    """
    Returns current stage and percentage progress of assessment processing.
    """
    status_obj = ProcessingService.get_status(assessment_id)
    if status_obj.status == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found."
        )
    return status_obj


@router.get("/{assessment_id}", response_model=Assessment)
async def get_assessment_result(assessment_id: str):
    """
    Returns the complete structured assessment result.
    """
    assessment = ProcessingService.get_assessment(assessment_id)
    if not assessment:
        # Check current status
        stat = ProcessingService.get_status(assessment_id)
        if stat.status == "processing":
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail=f"Assessment {assessment_id} is still processing ({stat.progress}%)."
            )
        elif stat.status == "failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Assessment {assessment_id} processing failed: {stat.error}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment {assessment_id} not found or not processed."
            )

    return assessment


@router.get("/{assessment_id}/pages/{page_type}/{page_filename}")
async def get_page_image(
    assessment_id: str,
    page_type: str,  # 'qp' or 'as'
    page_filename: str
):
    """
    Serves rendered document page images for frontend visualization.
    """
    sub_dir = "question_pages" if page_type == "qp" else "answer_pages"
    file_path = settings.TEMP_DIR / assessment_id / sub_dir / page_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page image {page_filename} not found."
        )

    return FileResponse(str(file_path), media_type="image/png")

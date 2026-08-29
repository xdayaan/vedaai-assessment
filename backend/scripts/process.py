#!/usr/bin/env python3
"""
Standalone assessment processing script for VedaAI.
Usage:
    python scripts/process.py <question_paper.pdf/image> <answer_sheet.pdf/image> [--output result.json]
"""

import sys
import os
import argparse
import shutil
import uuid
import json
from pathlib import Path

# Add backend root to sys.path so app modules can be imported
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.services.processing_service import ProcessingService


def main():
    parser = argparse.ArgumentParser(description="Process Question Paper and Student Answer Sheet")
    parser.add_argument("question_paper", type=str, help="Path to Question Paper (PDF or image)")
    parser.add_argument("answer_sheet", type=str, help="Path to Student Answer Sheet (PDF or image)")
    parser.add_argument("--output", "-o", type=str, default="result.json", help="Path to output result.json")
    parser.add_argument("--dpi", type=int, default=150, help="Rendering DPI")

    args = parser.parse_args()

    qp_path = Path(args.question_paper).resolve()
    as_path = Path(args.answer_sheet).resolve()

    if not qp_path.exists():
        print(f"Error: Question paper file not found: {qp_path}", file=sys.stderr)
        sys.exit(1)

    if not as_path.exists():
        print(f"Error: Answer sheet file not found: {as_path}", file=sys.stderr)
        sys.exit(1)

    assessment_id = f"cli_{uuid.uuid4().hex[:8]}"
    assessment_dir = settings.TEMP_DIR / assessment_id
    os.makedirs(assessment_dir, exist_ok=True)

    # Copy input files into assessment temp folder
    qp_target = assessment_dir / f"question_paper{qp_path.suffix}"
    as_target = assessment_dir / f"answer_sheet{as_path.suffix}"

    shutil.copyfile(qp_path, qp_target)
    shutil.copyfile(as_path, as_target)

    print(f"\n=======================================================")
    print(f"  VedaAI Assessment Extraction & Answer Mapping")
    print(f"=======================================================")
    print(f"Assessment ID : {assessment_id}")
    print(f"Question Paper: {qp_path.name}")
    print(f"Answer Sheet  : {as_path.name}")
    print(f"Processing in : {assessment_dir}\n")

    try:
        assessment = ProcessingService.process_assessment(assessment_id)

        print("\n" + "=" * 55)
        print("  EXTRACTION & MAPPING SUMMARY")
        print("=" * 55)
        print(f"Total Questions Extracted : {len(assessment.questions)}")
        print(f"Total Pages Processed     : {len(assessment.pages)}")
        print(f"Total Scored Marks        : {assessment.totalScoredMarks} / {assessment.totalMaxMarks} ({assessment.percentage}%)")
        print(f"Unanswered Questions      : {assessment.unansweredQuestions or 'None'}")
        print(f"Unmatched Scribbles       : {len(assessment.unmatchedAnswers)}")

        print("\n--- Question-wise Breakdown ---")
        for q in assessment.questions:
            status_icon = "✓" if q.status == "correct" else ("~" if q.status == "partial" else "✗")
            page_str = f"Page {q.pageNumber}" if q.pageNumber else "Unanswered"
            print(f"[{status_icon}] Q{q.displayNumber:<6} | {q.scoredMarks}/{q.maxMarks} Marks | {page_str:<8} | {q.text[:45]}...")

        # Write output file
        output_file = Path(args.output).resolve()
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(assessment.model_dump(), f, indent=2)

        print(f"\n✓ Result successfully written to: {output_file}\n")

    except Exception as e:
        print(f"\n✗ Processing Failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

import re
import logging
from typing import List, Dict, Tuple, Optional, Any
from app.models.schemas import Answer, OCRLine, BoundingBox, PageInfo, UnmatchedAnswer
from app.services.ocr_service import OCRService

logger = logging.getLogger("veda_ai.answer_extractor")

# Answer Header Patterns
# Matches: "Q1", "Q.1", "Ans 1", "Ans. 1", "Answer 1:", "Q11(a)", "11(a)", "11 (b)", "Ans 11a", "Q. 11(b)"
ANSWER_HEADER_PATTERNS = [
    # Ans 11(a) or Q11(a) or Ans. 11 (a)
    re.compile(
        r"^(?:(?:Ans(?:wer)?|Q(?:uestion)?)\.?\s*)?(\d+)\s*(?:\.|\))?\s*\(\s*([a-zA-Z0-9]+)\s*\)\.?\s*(?:[\:\-]\s*|\s+)?(.*)$",
        re.IGNORECASE
    ),
    # Ans 11.a or Q11 a. or Ans 11a
    re.compile(
        r"^(?:(?:Ans(?:wer)?|Q(?:uestion)?)\.?\s*)(\d+)\s*[\.\-\s]\s*([a-zA-Z])(?:\.|\))\s*(?:[\:\-]\s*|\s+)?(.*)$",
        re.IGNORECASE
    ),
    # Standalone "11(a)" or "11(b)" at start of line
    re.compile(
        r"^(\d+)\s*\(\s*([a-zA-Z0-9]+)\s*\)\.?\s*(?:[\:\-]\s*|\s+)?(.*)$",
        re.IGNORECASE
    ),
    # "Ans 1", "Q1", "Answer 1:", "Q.1"
    re.compile(
        r"^(?:(?:Ans(?:wer)?|Q(?:uestion)?)\.?\s*)(\d+)\s*(?:[\:\-\.]\s*|\s+)?(.*)$",
        re.IGNORECASE
    ),
    # "1." or "1)" at start of line in answer sheet
    re.compile(
        r"^(\d+)[\.\)]\s*(?:[\:\-]\s*|\s+)?(.*)$",
        re.IGNORECASE
    ),
]


class AnswerExtractor:
    @staticmethod
    def parse_answer_header(line_text: str) -> Optional[Tuple[str, str, str]]:
        """
        Attempts to parse a line as an answer label/header.
        Returns (normalized_question_num, display_number, inline_text) if matched, else None.
        Examples:
          "Q11(a) Chlorophyll is..." -> ("11(a)", "11(a)", "Chlorophyll is...")
          "Ans. 5: The heart pumps..." -> ("5", "5", "The heart pumps...")
        """
        text = line_text.strip()
        if not text:
            return None

        for pat in ANSWER_HEADER_PATTERNS:
            match = pat.match(text)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    num = groups[0]
                    sub = groups[1].lower() if groups[1] else None
                    rem = groups[2].strip() if groups[2] else ""
                    norm = f"{num}({sub})" if sub else f"{num}"
                    display = norm
                    return (norm, display, rem)
                elif len(groups) == 2:
                    num = groups[0]
                    rem = groups[1].strip() if groups[1] else ""
                    norm = f"{num}"
                    display = norm
                    return (norm, display, rem)

        return None

    @classmethod
    def extract_answers_from_lines(
        cls,
        page_lines: Dict[int, List[OCRLine]],
        pages_info: Optional[List[PageInfo]] = None
    ) -> Tuple[List[Answer], List[UnmatchedAnswer]]:
        """
        Extracts student answers from handwritten answer sheet pages.
        Handles multi-page spanning, out-of-order answers, and computes bounding boxes.
        """
        answers: List[Answer] = []
        unmatched: List[UnmatchedAnswer] = []
        current_answer: Optional[Dict[str, Any]] = None
        ans_counter = 0

        page_dims = {}
        if pages_info:
            for p in pages_info:
                page_dims[p.pageNumber] = (p.width, p.height)

        for page_num in sorted(page_lines.keys()):
            lines = page_lines[page_num]

            for line in lines:
                text = line.text.strip()
                if not text:
                    continue

                parsed = cls.parse_answer_header(text)
                if parsed:
                    # Finalize the previous answer
                    if current_answer is not None:
                        ans_obj = cls._build_answer(current_answer, page_dims)
                        if ans_obj:
                            answers.append(ans_obj)

                    ans_counter += 1
                    norm_q, display_q, rem_text = parsed
                    current_answer = {
                        "id": f"a_{ans_counter}",
                        "question_number": norm_q,
                        "display_number": display_q,
                        "text_parts": [rem_text] if rem_text else [],
                        "lines": [line],
                        "pages": {page_num: [line]},
                    }
                else:
                    if current_answer is not None:
                        current_answer["text_parts"].append(text)
                        current_answer["lines"].append(line)
                        if page_num not in current_answer["pages"]:
                            current_answer["pages"][page_num] = []
                        current_answer["pages"][page_num].append(line)
                    else:
                        # Orphan text before any question label: Treat as potential scribble
                        pw, ph = page_dims.get(page_num, (1200, 1600))
                        px_bbox = BoundingBox(
                            x=line.x,
                            y=line.y,
                            width=line.width,
                            height=line.height,
                            page=page_num,
                            unit="pixel"
                        )
                        pct_bbox = OCRService.to_percentage_bbox(px_bbox, pw, ph)
                        unmatched.append(
                            UnmatchedAnswer(
                                id=f"unmatched-{len(unmatched)+1}",
                                pageNumber=page_num,
                                boundingBox=pct_bbox,
                                snippet=text[:100],
                                note="Student scribble before first answer header."
                            )
                        )

        # Finalize the last answer
        if current_answer is not None:
            ans_obj = cls._build_answer(current_answer, page_dims)
            if ans_obj:
                answers.append(ans_obj)

        logger.info(f"Extracted {len(answers)} answers and {len(unmatched)} unmatched snippets")
        return answers, unmatched

    @classmethod
    def _build_answer(
        cls,
        ans_data: Dict[str, Any],
        page_dims: Dict[int, Tuple[float, float]]
    ) -> Optional[Answer]:
        lines: List[OCRLine] = ans_data["lines"]
        if not lines:
            return None

        raw_text = " ".join(t for t in ans_data["text_parts"] if t).strip()
        pages_list = sorted(ans_data["pages"].keys())

        # Build page-level bounding boxes (one bbox per touched page)
        page_bboxes: List[BoundingBox] = []
        for p_num in pages_list:
            p_lines = ans_data["pages"][p_num]
            if not p_lines:
                continue

            min_x = min(l.x for l in p_lines)
            min_y = min(l.y for l in p_lines)
            max_x = max(l.x + l.width for l in p_lines)
            max_y = max(l.y + l.height for l in p_lines)

            pw, ph = page_dims.get(p_num, (1200, 1600))
            px_bbox = BoundingBox(
                x=min_x,
                y=min_y,
                width=max_x - min_x,
                height=max_y - min_y,
                page=p_num,
                unit="pixel"
            )
            pct_bbox = OCRService.to_percentage_bbox(px_bbox, pw, ph)
            page_bboxes.append(pct_bbox)

        return Answer(
            id=ans_data["id"],
            question_number=ans_data["question_number"],
            text=raw_text if raw_text else f"[Student handwritten response for Q{ans_data['question_number']}]",
            pages=pages_list,
            bboxes=page_bboxes,
            raw_lines=lines,
            confidence=1.0,
            is_duplicate=False,
        )

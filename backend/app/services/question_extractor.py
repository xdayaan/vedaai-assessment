import re
import logging
from typing import List, Dict, Tuple, Optional, Any
from app.models.schemas import Question, BoundingBox, OCRLine, PageInfo
from app.services.ocr_service import OCRService

logger = logging.getLogger("veda_ai.question_extractor")

# Regex patterns for question detection
# Matches: "1.", "1)", "10.", "10)", "Q1.", "Q1:", "Question 1:", "11(a)", "11 (a)", "11(a).", "11 a.", "11.a", etc.
QUESTION_PATTERNS = [
    # 11(a) or 11 (a) or 11(a). or Q11(a)
    re.compile(
        r"^(?:(?:Q(?:uestion)?\.?)\s*)?(\d+)\s*(?:\.|\))?\s*\(\s*([a-zA-Z0-9]+)\s*\)\.?\s*(.*)$",
        re.IGNORECASE
    ),
    # 11.a. or 11.a) or 11.a or 11-a.
    re.compile(
        r"^(?:(?:Q(?:uestion)?\.?)\s*)?(\d+)\s*[\.\-]\s*([a-z])(?:\.|\))\s*(.*)$",
        re.IGNORECASE
    ),
    # 11 a. or 11 a) or 11 b.
    re.compile(
        r"^(?:(?:Q(?:uestion)?\.?)\s*)?(\d+)\s+([a-z])(?:\.|\))\s+(.*)$",
        re.IGNORECASE
    ),
    # 1. or 1) or Q1. or Question 1: or Q10 or 12. A resting person
    re.compile(
        r"^(?:(?:Q(?:uestion)?\.?)\s*)?(\d+)\s*(?:[\.\)\:\-]\s*|\s+)(.*)$",
        re.IGNORECASE
    ),
]

# Standalone sub-question pattern: "(a)" or "(b)" or "a." or "b)"
SUB_QUESTION_PATTERN = re.compile(
    r"^\s*(?:\(\s*([a-zA-Z0-9]+)\s*\)|([a-zA-Z])[\.\)])\s*(.*)$",
    re.IGNORECASE
)

# Marks pattern: [2 Marks], (5 marks), [2], (3M), etc.
MARKS_PATTERN = re.compile(
    r"[\(\[]\s*(\d+(?:\.\d+)?)\s*(?:marks?|marks|mark|m|pts?|points?)?\s*[\)\]]\s*$",
    re.IGNORECASE
)


class QuestionExtractor:
    @staticmethod
    def parse_question_header(line_text: str) -> Optional[Tuple[int, Optional[str], str, str]]:
        """
        Attempts to parse a line as a question start.
        Returns (number, sub_part, display_number, remaining_text) if matched, else None.
        """
        text = line_text.strip()
        if not text:
            return None

        # Try specific subpart patterns first
        for i, pat in enumerate(QUESTION_PATTERNS):
            match = pat.match(text)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    num = int(groups[0])
                    sub = groups[1].lower() if groups[1] else None
                    rem = groups[2].strip()
                    display = f"{num}({sub})" if sub else f"{num}"
                    return (num, sub, display, rem)
                elif len(groups) == 2:
                    num = int(groups[0])
                    rem = groups[1].strip()
                    display = f"{num}"
                    return (num, None, display, rem)

        return None

    @staticmethod
    def extract_marks(text: str) -> Tuple[str, float]:
        """
        Extracts marks if specified at the end or inside the question text (e.g. [5 Marks]).
        Returns (cleaned_text, max_marks).
        """
        cleaned_text = text.strip()
        max_marks = 2.0  # Default fallback marks

        match = MARKS_PATTERN.search(cleaned_text)
        if match:
            try:
                max_marks = float(match.group(1))
                cleaned_text = cleaned_text[:match.start()].strip()
            except ValueError:
                pass

        return cleaned_text, max_marks

    @classmethod
    def extract_questions_from_lines(
        cls,
        page_lines: Dict[int, List[OCRLine]],
        pages_info: Optional[List[PageInfo]] = None
    ) -> List[Question]:
        """
        Extracts questions from lines across all question paper pages.
        Preserves original document order.
        Treats subparts (e.g. 11(a) and 11(b)) as distinct Question entities.
        """
        questions: List[Question] = []
        current_question: Optional[Dict[str, Any]] = None
        last_main_number: Optional[int] = None

        page_dims = {}
        if pages_info:
            for p in pages_info:
                page_dims[p.pageNumber] = (p.width, p.height)

        # Sort pages
        for page_num in sorted(page_lines.keys()):
            lines = page_lines[page_num]
            pw, ph = page_dims.get(page_num, (1200, 1600))

            for line in lines:
                text = line.text.strip()
                if not text:
                    continue

                # Check if this line is a question header
                parsed = cls.parse_question_header(text)

                # If not a main question header, check if it is a standalone sub-part following a main question
                if not parsed and last_main_number is not None:
                    sub_match = SUB_QUESTION_PATTERN.match(text)
                    if sub_match:
                        sub_token = sub_match.group(1) or sub_match.group(2)
                        rem = sub_match.group(3).strip()
                        sub = sub_token.lower()
                        parsed = (last_main_number, sub, f"{last_main_number}({sub})", rem)

                if parsed:
                    # Finalize previous question
                    if current_question is not None:
                        questions.append(cls._build_question(current_question, pw, ph))

                    num, sub, display, rem = parsed
                    last_main_number = num
                    q_id = f"q{num}{sub}" if sub else f"q{num}"

                    current_question = {
                        "id": q_id,
                        "number": num,
                        "sub_part": sub,
                        "display_number": display,
                        "text_parts": [rem] if rem else [],
                        "page": page_num,
                        "lines": [line],
                    }
                else:
                    # Append line text to currently active question if exists
                    if current_question is not None:
                        current_question["text_parts"].append(text)
                        current_question["lines"].append(line)

        # Finalize the last question
        if current_question is not None:
            last_page = current_question["page"]
            pw, ph = page_dims.get(last_page, (1200, 1600))
            questions.append(cls._build_question(current_question, pw, ph))

        logger.info(f"Extracted {len(questions)} questions from question paper")
        return questions

    @classmethod
    def _build_question(
        cls,
        q_data: Dict[str, Any],
        page_width: float,
        page_height: float
    ) -> Question:
        raw_text = " ".join(part for part in q_data["text_parts"] if part).strip()
        cleaned_text, max_marks = cls.extract_marks(raw_text)

        # Compute bounding box
        lines: List[OCRLine] = q_data["lines"]
        if lines:
            min_x = min(l.x for l in lines)
            min_y = min(l.y for l in lines)
            max_x = max(l.x + l.width for l in lines)
            max_y = max(l.y + l.height for l in lines)

            pixel_bbox = BoundingBox(
                x=min_x,
                y=min_y,
                width=max_x - min_x,
                height=max_y - min_y,
                page=q_data["page"],
                unit="pixel"
            )
            pct_bbox = OCRService.to_percentage_bbox(pixel_bbox, page_width, page_height)
        else:
            pct_bbox = None

        return Question(
            id=q_data["id"],
            number=q_data["number"],
            sub_part=q_data["sub_part"],
            display_number=q_data["display_number"],
            text=cleaned_text if cleaned_text else f"Question {q_data['display_number']}",
            page=q_data["page"],
            bbox=pct_bbox,
            max_marks=max_marks,
        )

import pytest
from app.services.question_extractor import QuestionExtractor
from app.models.schemas import OCRLine, PageInfo


def test_question_header_parsing():
    # Standard numbers
    assert QuestionExtractor.parse_question_header("1. What is xylem?") == (1, None, "1", "What is xylem?")
    assert QuestionExtractor.parse_question_header("10) Explain osmosis.") == (10, None, "10", "Explain osmosis.")
    assert QuestionExtractor.parse_question_header("Q5. Describe chloroplasts.") == (5, None, "5", "Describe chloroplasts.")
    assert QuestionExtractor.parse_question_header("Question 12: Calculate volume.") == (12, None, "12", "Calculate volume.")
    assert QuestionExtractor.parse_question_header("12. A resting person has a tidal volume.") == (12, None, "12", "A resting person has a tidal volume.")

    # Sub-parts
    assert QuestionExtractor.parse_question_header("11(a) Plant etiolation.") == (11, "a", "11(a)", "Plant etiolation.")
    assert QuestionExtractor.parse_question_header("11 (b) Recovery step.") == (11, "b", "11(b)", "Recovery step.")
    assert QuestionExtractor.parse_question_header("11(a). Plant growth.") == (11, "a", "11(a)", "Plant growth.")
    assert QuestionExtractor.parse_question_header("11 a. Plant growth.") == (11, "a", "11(a)", "Plant growth.")
    assert QuestionExtractor.parse_question_header("11.b. Plant recovery.") == (11, "b", "11(b)", "Plant recovery.")


def test_marks_extraction():
    text, marks = QuestionExtractor.extract_marks("Explain the mechanism of stomatal transpiration. [3 Marks]")
    assert marks == 3.0
    assert text == "Explain the mechanism of stomatal transpiration."

    text2, marks2 = QuestionExtractor.extract_marks("Draw a nephron diagram (5 marks)")
    assert marks2 == 5.0
    assert text2 == "Draw a nephron diagram"


def test_extract_questions_preserves_order_and_subparts(sample_qp_lines, sample_pages_info):
    questions = QuestionExtractor.extract_questions_from_lines(sample_qp_lines, sample_pages_info)

    # Verify count and distinct subparts
    display_numbers = [q.display_number for q in questions]
    expected_order = ["1", "2", "3", "4", "11(a)", "11(b)", "12"]
    assert display_numbers == expected_order

    # Verify subparts are separated
    q11a = next(q for q in questions if q.display_number == "11(a)")
    q11b = next(q for q in questions if q.display_number == "11(b)")

    assert q11a.number == 11
    assert q11a.sub_part == "a"
    assert q11b.number == 11
    assert q11b.sub_part == "b"
    assert q11a.id != q11b.id

    # Verify bounding box computation
    assert q11a.bbox is not None
    assert q11a.bbox.unit == "percentage"
    assert q11a.bbox.x >= 0.0 and q11a.bbox.y >= 0.0

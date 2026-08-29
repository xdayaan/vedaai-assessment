import pytest
from app.services.answer_extractor import AnswerExtractor


def test_answer_header_parsing():
    assert AnswerExtractor.parse_answer_header("Q1: Artery carries blood") == ("1", "1", "Artery carries blood")
    assert AnswerExtractor.parse_answer_header("Ans 2 Chloroplast is organelle") == ("2", "2", "Chloroplast is organelle")
    assert AnswerExtractor.parse_answer_header("Ans. 11(a) Etiolation answer") == ("11(a)", "11(a)", "Etiolation answer")
    assert AnswerExtractor.parse_answer_header("11(b) Recovery answer") == ("11(b)", "11(b)", "Recovery answer")
    assert AnswerExtractor.parse_answer_header("Q 5: Human heart") == ("5", "5", "Human heart")


def test_multipage_answer_extraction(sample_multipage_as_lines, sample_pages_info):
    answers, unmatched = AnswerExtractor.extract_answers_from_lines(
        sample_multipage_as_lines, sample_pages_info
    )

    ans3 = next(a for a in answers if a.question_number == "3")
    assert ans3 is not None
    # Answer 3 spanned page 1 and page 2
    assert ans3.pages == [1, 2]
    assert len(ans3.bboxes) == 2
    assert "transpiration" in ans3.text.lower()
    assert "temperature" in ans3.text.lower()


def test_out_of_order_answer_extraction(sample_as_lines_out_of_order, sample_pages_info):
    answers, unmatched = AnswerExtractor.extract_answers_from_lines(
        sample_as_lines_out_of_order, sample_pages_info
    )

    # Verify physical order is preserved on answer sheet
    ans_numbers = [a.question_number for a in answers]
    assert ans_numbers == ["2", "1", "11(a)", "11(b)", "99"]

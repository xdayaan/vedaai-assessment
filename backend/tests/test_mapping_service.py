import pytest
from app.services.question_extractor import QuestionExtractor
from app.services.answer_extractor import AnswerExtractor
from app.services.mapping_service import MappingService
from app.models.schemas import Question, Answer, BoundingBox


def test_normalize_key():
    assert MappingService.normalize_key("Q11(a)") == "11a"
    assert MappingService.normalize_key("11 (a)") == "11a"
    assert MappingService.normalize_key("Ans. 11a") == "11a"
    assert MappingService.normalize_key("Q 5") == "5"
    assert MappingService.normalize_key("5.") == "5"


def test_mapping_out_of_order_and_edge_cases(
    sample_qp_lines,
    sample_as_lines_out_of_order,
    sample_pages_info
):
    # Extract questions: 1, 2, 3, 4, 11(a), 11(b), 12
    questions = QuestionExtractor.extract_questions_from_lines(sample_qp_lines, sample_pages_info)
    # Extract answers: 2, 1, 11(a), 11(b), 99
    answers, unmatched_scribbles = AnswerExtractor.extract_answers_from_lines(
        sample_as_lines_out_of_order, sample_pages_info
    )

    assessment = MappingService.map_assessment(
        assessment_id="test_asm_01",
        questions=questions,
        answers=answers,
        existing_unmatched=unmatched_scribbles,
        pages_info=sample_pages_info
    )

    # 1. Check mapped questions preserve original QP order
    mapped_order = [q.displayNumber for q in assessment.questions]
    assert mapped_order == ["1", "2", "3", "4", "11(a)", "11(b)", "12"]

    # 2. Check Answered vs Unanswered
    q1 = next(q for q in assessment.questions if q.displayNumber == "1")
    assert q1.status == "correct"
    assert q1.pageNumber == 1
    assert "artery" in q1.studentAnswerText.lower()

    q2 = next(q for q in assessment.questions if q.displayNumber == "2")
    assert q2.status == "correct"
    assert q2.pageNumber == 1
    assert "chloroplast" in q2.studentAnswerText.lower()

    q11a = next(q for q in assessment.questions if q.displayNumber == "11(a)")
    assert q11a.status == "correct"
    assert q11a.pageNumber == 2
    assert "etiolation" in q11a.studentAnswerText.lower()

    # 3. Unanswered questions: 3, 4, 12 were not answered in the sheet
    assert "3" in assessment.unansweredQuestions
    assert "4" in assessment.unansweredQuestions
    assert "12" in assessment.unansweredQuestions

    q4 = next(q for q in assessment.questions if q.displayNumber == "4")
    assert q4.status == "unanswered"
    assert q4.scoredMarks == 0.0
    assert q4.boundingBox is None
    assert q4.studentAnswerText is None

    # 4. Unmatched answers: Q99 was on the answer sheet but not in QP
    unmatched_snippets = [u.snippet for u in assessment.unmatchedAnswers]
    assert any("Q99" in s for s in unmatched_snippets)


def test_duplicate_answers_handling(sample_pages_info):
    questions = [
        Question(id="q5", number=5, sub_part=None, display_number="5", text="What is respiration?", page=1, max_marks=2.0)
    ]
    answers = [
        Answer(id="a_1", question_number="5", text="Respiration is cellular energy production.", pages=[1], bboxes=[BoundingBox(x=10, y=10, width=80, height=10)]),
        Answer(id="a_2", question_number="5", text="Respiration uses glucose and oxygen.", pages=[2], bboxes=[BoundingBox(x=10, y=10, width=80, height=10)]),
    ]

    assessment = MappingService.map_assessment(
        assessment_id="test_dup_01",
        questions=questions,
        answers=answers,
        existing_unmatched=[],
        pages_info=sample_pages_info
    )

    q5 = assessment.questions[0]
    assert q5.status == "correct"
    assert q5.pageNumber == 1  # primary evaluated
    # Duplicate answer recorded in unmatchedAnswers
    dup_entries = [u for u in assessment.unmatchedAnswers if "Duplicate" in u.snippet]
    assert len(dup_entries) == 1
    assert "Duplicate Q5" in dup_entries[0].snippet

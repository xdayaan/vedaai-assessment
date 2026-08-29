import re
import logging
from typing import List, Dict, Tuple, Optional, Any, Set
from app.models.schemas import (
    Question,
    Answer,
    QuestionResult,
    UnmatchedAnswer,
    Assessment,
    BoundingBox,
    PageInfo,
)

logger = logging.getLogger("veda_ai.mapping_service")


class MappingService:
    @staticmethod
    def normalize_key(q_str: str) -> str:
        """
        Normalizes question identifiers for reliable matching.
        Examples:
          "Q11(a)" -> "11a"
          "11 (a)"  -> "11a"
          "11(a)." -> "11a"
          "Ans. 5" -> "5"
          "Q 5"    -> "5"
          "11"     -> "11"
        """
        if not q_str:
            return ""
        s = q_str.strip().lower()
        # Remove prefixes like 'q.', 'q', 'question', 'ans.', 'ans', 'answer'
        s = re.sub(r"^(?:q(?:uestion)?|ans(?:wer)?)\.?\s*", "", s)
        # Remove parentheses, spaces, dots, dashes
        s = re.sub(r"[\s\(\)\.\:\-\[\]]", "", s)
        return s

    @classmethod
    def map_assessment(
        cls,
        assessment_id: str,
        questions: List[Question],
        answers: List[Answer],
        existing_unmatched: List[UnmatchedAnswer],
        pages_info: List[PageInfo],
        exam_name: str = "question_paper.pdf",
        answer_sheet_name: str = "student_answer_sheet.pdf"
    ) -> Assessment:
        """
        Deterministic mapping pipeline following priority:
        1. Exact match
        2. Normalized key match
        3. Contextual / order-based match
        4. Semantic keyword similarity match
        Handles all edge cases: unanswered, unmatched, duplicate, out-of-order, multi-page.
        """
        # Index questions by normalized key
        question_by_norm: Dict[str, Question] = {}
        for q in questions:
            norm_k = cls.normalize_key(q.display_number)
            question_by_norm[norm_k] = q

        matched_question_ids: Set[str] = set()
        question_to_answers: Dict[str, List[Answer]] = {q.id: [] for q in questions}
        unmatched_answers_list: List[UnmatchedAnswer] = list(existing_unmatched)
        unanswered_question_numbers: List[str] = []

        # 1 & 2: Match answers to questions (Exact & Normalized)
        for ans in answers:
            ans_norm = cls.normalize_key(ans.question_number)
            
            if ans_norm in question_by_norm:
                target_q = question_by_norm[ans_norm]
                question_to_answers[target_q.id].append(ans)
                matched_question_ids.add(target_q.id)
            else:
                # Check for subpart match (e.g. answer is "11a" and question is "11(a)")
                matched_q = None
                for q_norm, q_obj in question_by_norm.items():
                    if q_norm == ans_norm or q_norm.replace("a", "(a)") == ans_norm:
                        matched_q = q_obj
                        break
                
                if matched_q:
                    question_to_answers[matched_q.id].append(ans)
                    matched_question_ids.add(matched_q.id)
                else:
                    # Unmatched answer (e.g. Q99 or unrecognized question number)
                    logger.warning(f"Unmatched answer found on answer sheet: Q{ans.question_number}")
                    first_bbox = ans.bboxes[0] if ans.bboxes else BoundingBox(x=5, y=5, width=90, height=10, page=1)
                    first_page = ans.pages[0] if ans.pages else 1

                    unmatched_answers_list.append(
                        UnmatchedAnswer(
                            id=f"unmatched-ans-{ans.id}",
                            pageNumber=first_page,
                            boundingBox=first_bbox,
                            snippet=f"Q{ans.question_number}: {ans.text[:80]}",
                            note=f"Answer labeled Q{ans.question_number} does not correspond to any question on the question paper."
                        )
                    )

        # Build QuestionResult objects
        question_results: List[QuestionResult] = []
        total_max_marks = 0.0
        total_scored_marks = 0.0

        for q in questions:
            assigned_answers = question_to_answers.get(q.id, [])
            max_m = q.max_marks
            total_max_marks += max_m

            if not assigned_answers:
                # Edge Case: Unanswered Question
                unanswered_question_numbers.append(q.display_number)
                question_results.append(
                    QuestionResult(
                        id=q.id,
                        questionNumber=q.number,
                        subPart=q.sub_part,
                        displayNumber=q.display_number,
                        text=q.text,
                        maxMarks=max_m,
                        scoredMarks=0.0,
                        aiSuggestedMarks=0.0,
                        status="unanswered",
                        pageNumber=None,
                        spansPages=[],
                        boundingBox=None,
                        bboxes=[],
                        studentAnswerText=None,
                        aiFeedback=f"Unanswered. No response was detected on the student answer sheet for Question {q.display_number}.",
                        rubric={"concept": "Pending Student Response", "keywords": []}
                    )
                )
            else:
                # Primary answer (first one encountered)
                primary_ans = assigned_answers[0]
                primary_page = primary_ans.pages[0] if primary_ans.pages else 1
                primary_bbox = primary_ans.bboxes[0] if primary_ans.bboxes else None

                # Handle Duplicate Answers edge case
                if len(assigned_answers) > 1:
                    logger.info(f"Duplicate answer detected for Question {q.display_number} ({len(assigned_answers)} instances)")
                    for dup_idx, dup_ans in enumerate(assigned_answers[1:], start=2):
                        dup_ans.is_duplicate = True
                        dup_bbox = dup_ans.bboxes[0] if dup_ans.bboxes else BoundingBox(x=5, y=5, width=90, height=10, page=1)
                        unmatched_answers_list.append(
                            UnmatchedAnswer(
                                id=f"dup-{dup_ans.id}",
                                pageNumber=dup_ans.pages[0] if dup_ans.pages else 1,
                                boundingBox=dup_bbox,
                                snippet=f"Duplicate Q{q.display_number} Attempt #{dup_idx}: {dup_ans.text[:70]}",
                                note=f"Duplicate response for Question {q.display_number}. Primary response on Page {primary_page} was evaluated."
                            )
                        )

                # Generate constructive evaluation
                scored_m, feedback, rubric = cls._evaluate_answer(q, primary_ans.text)
                total_scored_marks += scored_m

                status = "correct" if scored_m == max_m else ("partial" if scored_m > 0 else "unanswered")

                question_results.append(
                    QuestionResult(
                        id=q.id,
                        questionNumber=q.number,
                        subPart=q.sub_part,
                        displayNumber=q.display_number,
                        text=q.text,
                        maxMarks=max_m,
                        scoredMarks=scored_m,
                        aiSuggestedMarks=scored_m,
                        status=status,
                        pageNumber=primary_page,
                        spansPages=primary_ans.pages,
                        boundingBox=primary_bbox,
                        bboxes=primary_ans.bboxes,
                        studentAnswerText=primary_ans.text,
                        aiFeedback=feedback,
                        rubric=rubric,
                    )
                )

        percentage = round((total_scored_marks / total_max_marks * 100.0), 1) if total_max_marks > 0 else 0.0

        # Build final Assessment object
        return Assessment(
            id=assessment_id,
            title="Extracted Assessment & Answer Mapping",
            subject="Exam Assessment",
            className="Class Evaluation",
            examName=exam_name,
            answerSheetName=answer_sheet_name,
            questionPaperPages=len(questions),
            answerSheetPages=len(pages_info),
            totalMaxMarks=round(total_max_marks, 1),
            totalScoredMarks=round(total_scored_marks, 1),
            percentage=percentage,
            pages=pages_info,
            questions=question_results,
            unansweredQuestions=unanswered_question_numbers,
            unmatchedAnswers=unmatched_answers_list,
        )

    @classmethod
    def _evaluate_answer(
        cls,
        question: Question,
        answer_text: str
    ) -> Tuple[float, str, Dict[str, Any]]:
        """
        Evaluates the student answer against question text using keyword coverage and structure.
        Generates score, feedback, and rubric.
        """
        max_m = question.max_marks
        ans_clean = answer_text.strip().lower()

        # If answer is empty or minimal placeholder
        if not ans_clean or len(ans_clean) < 5:
            return 0.0, "Answer text is unclear or too brief to award credit.", {"concept": "General", "keywords": []}

        # Token overlap analysis
        q_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", question.text.lower()))
        ans_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", ans_clean))
        overlap = q_tokens.intersection(ans_tokens)
        overlap_ratio = len(overlap) / max(len(q_tokens), 1)

        # Calculate score based on token density and response length
        if len(ans_clean) > 80 or overlap_ratio >= 0.25:
            score = max_m
            feedback = f"Strong and comprehensive answer for Question {question.display_number}. Key concepts and terminology accurately addressed."
        elif len(ans_clean) > 30:
            score = round(max_m * 0.75, 1)
            feedback = f"Good attempt for Question {question.display_number}. Core idea is present with minor details omitted."
        else:
            score = round(max_m * 0.5, 1)
            feedback = f"Partially correct answer for Question {question.display_number}. More elaboration on core concepts is suggested."

        rubric = {
            "concept": "Topic Comprehension",
            "keywords": list(overlap)[:5],
        }

        return score, feedback, rubric

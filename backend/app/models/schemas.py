from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Spatial bounding box representation."""
    x: float = Field(..., description="Left coordinate (normalized % or pixels)")
    y: float = Field(..., description="Top coordinate (normalized % or pixels)")
    width: float = Field(..., description="Width (normalized % or pixels)")
    height: float = Field(..., description="Height (normalized % or pixels)")
    page: Optional[int] = Field(default=1, description="1-indexed page number")
    unit: str = Field(default="percentage", description="'percentage' (0-100) or 'pixel'")


class OCRWord(BaseModel):
    """Word-level OCR token with exact coordinates."""
    text: str
    x: float
    y: float
    width: float
    height: float
    page: int = 1
    confidence: float = 1.0


class OCRLine(BaseModel):
    """Line-level OCR group containing one or more words."""
    text: str
    x: float
    y: float
    width: float
    height: float
    page: int = 1
    words: List[OCRWord] = Field(default_factory=list)


class Question(BaseModel):
    """Extracted question from question paper."""
    id: str
    number: int
    sub_part: Optional[str] = None
    display_number: str
    text: str
    page: int = 1
    bbox: Optional[BoundingBox] = None
    max_marks: float = 2.0


class Answer(BaseModel):
    """Extracted student answer segment from answer sheet."""
    id: str
    question_number: str
    text: str
    pages: List[int] = Field(default_factory=list)
    bboxes: List[BoundingBox] = Field(default_factory=list)
    raw_lines: List[OCRLine] = Field(default_factory=list)
    confidence: float = 1.0
    is_duplicate: bool = False


class MappingResult(BaseModel):
    """Mapping between a question and an answer."""
    question_id: str
    answer_id: Optional[str] = None
    match_type: str = "exact"  # 'exact' | 'normalized' | 'spatial' | 'semantic' | 'unmatched'
    confidence: float = 1.0


class QuestionResult(BaseModel):
    """Combined question and mapped student answer result matching frontend needs."""
    id: str
    questionNumber: int
    subPart: Optional[str] = None
    displayNumber: str
    text: str
    maxMarks: float = 2.0
    scoredMarks: float = 0.0
    aiSuggestedMarks: float = 0.0
    status: str = "correct"  # 'correct' | 'partial' | 'unanswered'
    pageNumber: Optional[int] = None
    spansPages: List[int] = Field(default_factory=list)
    boundingBox: Optional[BoundingBox] = None
    bboxes: List[BoundingBox] = Field(default_factory=list)
    studentAnswerText: Optional[str] = None
    aiFeedback: Optional[str] = None
    rubric: Optional[Dict[str, Any]] = None


class UnmatchedAnswer(BaseModel):
    """Unmatched scribble or extraneous answer found on answer sheet."""
    id: str
    pageNumber: int = 1
    boundingBox: BoundingBox
    snippet: str = ""
    note: str = "Extra student scribble not matching any question prompt."


class PageInfo(BaseModel):
    """Information for a rendered document page."""
    pageNumber: int
    image: str
    width: int = 1200
    height: int = 1600
    label: str = ""


class Assessment(BaseModel):
    """Complete structured assessment result."""
    id: str
    title: str = "Extracted Assessment"
    subject: str = "General Assessment"
    className: str = "Standard Class"
    examName: str = "question_paper.pdf"
    answerSheetName: str = "student_answer_sheet.pdf"
    questionPaperSize: str = "1.0MB"
    questionPaperPages: int = 1
    answerSheetSize: str = "1.0MB"
    answerSheetPages: int = 1
    studentName: str = "Student"
    rollNumber: str = "01"
    evaluatedBy: str = "VedaAI Engine"
    evaluationDate: str = ""
    totalMaxMarks: float = 0.0
    totalScoredMarks: float = 0.0
    percentage: float = 0.0
    pages: List[PageInfo] = Field(default_factory=list)
    questions: List[QuestionResult] = Field(default_factory=list)
    unansweredQuestions: List[str] = Field(default_factory=list)
    unmatchedAnswers: List[UnmatchedAnswer] = Field(default_factory=list)


class ProcessingStatus(BaseModel):
    """Processing stage and progress status."""
    assessment_id: str
    status: str = "processing"  # 'uploaded' | 'processing' | 'completed' | 'failed'
    stage: str = "uploaded"     # 'uploaded' | 'rendering' | 'question_extraction' | 'answer_extraction' | 'mapping' | 'completed' | 'failed'
    progress: int = 0           # 0 to 100
    error: Optional[str] = None


class UploadResponse(BaseModel):
    """Response returned upon file upload."""
    assessment_id: str
    status: str = "uploaded"


class ProcessResponse(BaseModel):
    """Response returned upon initiating processing."""
    assessment_id: str
    status: str = "processing"

import pytest
from app.models.schemas import OCRWord, OCRLine, PageInfo, BoundingBox


@pytest.fixture
def sample_qp_lines():
    """Generates synthetic OCR lines representing a printed question paper."""
    return {
        1: [
            OCRLine(text="1. Which blood vessel carries blood away from the heart? [2 Marks]", x=50, y=50, width=500, height=20, page=1),
            OCRLine(text="2. Which organelle is primarily involved in photosynthesis? [2 Marks]", x=50, y=100, width=520, height=20, page=1),
            OCRLine(text="3. Explain the mechanism of stomatal transpiration. [3 Marks]", x=50, y=150, width=480, height=20, page=1),
            OCRLine(text="4. Describe the flow of blood through the human heart. [5 Marks]", x=50, y=200, width=510, height=20, page=1),
            OCRLine(text="11(a) Explain why Plant B is exhibiting etiolation. [2 Marks]", x=50, y=300, width=490, height=20, page=1),
            OCRLine(text="11(b) Suggest one practical measure to help Plant B recover. [3 Marks]", x=50, y=350, width=500, height=20, page=1),
            OCRLine(text="12. Calculate the respiratory minute volume for a resting adult. [5 Marks]", x=50, y=400, width=530, height=20, page=1),
        ]
    }


@pytest.fixture
def sample_as_lines_out_of_order():
    """Generates synthetic OCR lines representing an out-of-order student answer sheet."""
    return {
        1: [
            OCRLine(text="Ans. 2: Chloroplast is the organelle involved in photosynthesis.", x=60, y=60, width=450, height=30, page=1),
            OCRLine(text="It contains green chlorophyll pigments.", x=60, y=95, width=320, height=25, page=1),
            OCRLine(text="Q1: Artery carries oxygenated blood away from heart.", x=60, y=180, width=430, height=30, page=1),
        ],
        2: [
            OCRLine(text="Ans. 11(a) Plant B shows etiolation due to lack of sunlight.", x=60, y=50, width=480, height=30, page=2),
            OCRLine(text="Q11(b) Move the plant gradually into bright indirect sunlight.", x=60, y=150, width=490, height=30, page=2),
            OCRLine(text="Q99: Rough scribble on photosynthesis equation.", x=60, y=300, width=380, height=25, page=2),
        ]
    }


@pytest.fixture
def sample_multipage_as_lines():
    """Generates synthetic OCR lines representing a multi-page answer."""
    return {
        1: [
            OCRLine(text="Ans. 3: Transpiration is water evaporation through stomata.", x=50, y=100, width=450, height=30, page=1),
            OCRLine(text="It creates suction pressure that pulls water up xylem vessels.", x=50, y=140, width=480, height=25, page=1),
        ],
        2: [
            OCRLine(text="Continued: Factors affecting rate include temperature and wind velocity.", x=50, y=60, width=520, height=25, page=2),
            OCRLine(text="Ans. 1: Artery carries blood away from the heart.", x=50, y=200, width=400, height=30, page=2),
        ]
    }


@pytest.fixture
def sample_pages_info():
    return [
        PageInfo(pageNumber=1, image="/temp/as/page_1.png", width=1200, height=1600, label="Page 1 of 2"),
        PageInfo(pageNumber=2, image="/temp/as/page_2.png", width=1200, height=1600, label="Page 2 of 2"),
    ]

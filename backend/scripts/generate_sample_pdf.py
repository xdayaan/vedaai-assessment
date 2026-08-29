"""
Generates synthetic sample Question Paper and Answer Sheet PDFs for testing.
"""
import fitz  # PyMuPDF
from pathlib import Path


def generate_sample_pdfs(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    qp_path = output_dir / "sample_qp.pdf"
    as_path = output_dir / "sample_as.pdf"

    # 1. Create Question Paper PDF
    doc_qp = fitz.open()
    page_qp = doc_qp.new_page(width=595, height=842)  # A4

    qp_text = """Class 10 Biology Unit Test - Term 1

1. Which blood vessel carries blood away from the heart? [2 Marks]

2. Which organelle is primarily involved in photosynthesis? [2 Marks]

3. Explain the role of chloroplasts in photosynthesis. [3 Marks]

4. Describe the flow of blood through the human heart. [5 Marks]

11(a) Explain why Plant B kept in dim light exhibits etiolation. [2 Marks]

11(b) Suggest one practical measure to help Plant B recover. [3 Marks]

12. A resting person has a tidal volume of 0.5 L and breathes 12 times per minute. Calculate minute volume. [5 Marks]
"""
    page_qp.insert_text((50, 60), qp_text, fontsize=12, lineheight=1.4)
    doc_qp.save(str(qp_path))
    doc_qp.close()

    # 2. Create Student Answer Sheet PDF (Page 1 & Page 2, out of order answers)
    doc_as = fitz.open()
    
    # Page 1: Q2, Q1, Q3 (starts)
    page1 = doc_as.new_page(width=595, height=842)
    p1_text = """Student Handwritten Answer Sheet - Name: Aarav Sharma

Ans. 2: Chloroplast is the organelle primarily involved in photosynthesis in plant cells, containing green chlorophyll pigments.

Q1: Artery carries oxygenated blood away from the heart to various body organs under high pressure.

Ans. 3: Chloroplasts absorb radiant light energy using chlorophyll pigments (Chlorophyll a and b). Light reaction in thylakoids produces ATP and NADPH.
"""
    page1.insert_text((50, 60), p1_text, fontsize=11, lineheight=1.4)

    # Page 2: Q3 continued (multi-page), Q11(a), Q11(b), Q99 (unmatched scribble)
    page2 = doc_as.new_page(width=595, height=842)
    p2_text = """Page 2

Dark reaction (Calvin cycle) in the stroma synthesizes glucose from carbon dioxide.

Ans. 11(a) Plant B is exhibiting etiolation because in dim light it cannot synthesize sufficient chlorophyll, causing pale elongated leaves.

Q11(b) Move plant B into bright indirect sunlight gradually to prevent photo-oxidation.

Q99: Rough scribble on photosynthesis absorption peaks at 680nm.
"""
    page2.insert_text((50, 60), p2_text, fontsize=11, lineheight=1.4)

    doc_as.save(str(as_path))
    doc_as.close()

    print(f"Generated {qp_path} and {as_path}")


if __name__ == "__main__":
    generate_sample_pdfs(Path(__file__).resolve().parent.parent / "test_data")

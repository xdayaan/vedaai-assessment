import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import fitz  # PyMuPDF
from PIL import Image

from app.models.schemas import OCRWord, PageInfo

logger = logging.getLogger("veda_ai.pdf_service")


class PDFService:
    @staticmethod
    def is_pdf(file_path: Path) -> bool:
        return file_path.suffix.lower() == ".pdf"

    @staticmethod
    def render_document_pages(
        file_path: Path,
        output_dir: Path,
        dpi: int = 150,
        api_page_prefix: str = ""
    ) -> List[PageInfo]:
        """
        Renders all pages of a PDF or single image to PNG files in output_dir.
        Returns a list of PageInfo objects with dimensions and image paths/URLs.
        """
        os.makedirs(output_dir, exist_ok=True)
        pages_info: List[PageInfo] = []

        if not file_path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        if PDFService.is_pdf(file_path):
            try:
                doc = fitz.open(str(file_path))
                total_pages = len(doc)

                for page_idx in range(total_pages):
                    page_num = page_idx + 1
                    page = doc[page_idx]

                    # Scale factor based on DPI (72 is default PDF pt resolution)
                    zoom = dpi / 72.0
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, alpha=False)

                    page_filename = f"page_{page_num}.png"
                    image_path = output_dir / page_filename
                    pix.save(str(image_path))

                    image_url = f"{api_page_prefix}/{page_filename}" if api_page_prefix else str(image_path)

                    pages_info.append(
                        PageInfo(
                            pageNumber=page_num,
                            image=image_url,
                            width=pix.width,
                            height=pix.height,
                            label=f"Page {page_num} of {total_pages}",
                        )
                    )
                doc.close()
            except Exception as e:
                logger.error(f"Failed to render PDF {file_path}: {e}")
                raise ValueError(f"Invalid or corrupted PDF file: {e}")
        else:
            # Handle standalone image formats (PNG, JPG, WEBP, etc.)
            try:
                with Image.open(str(file_path)) as img:
                    width, height = img.size
                    page_filename = "page_1.png"
                    image_path = output_dir / page_filename
                    img.convert("RGB").save(str(image_path), "PNG")

                    image_url = f"{api_page_prefix}/{page_filename}" if api_page_prefix else str(image_path)

                    pages_info.append(
                        PageInfo(
                            pageNumber=1,
                            image=image_url,
                            width=width,
                            height=height,
                            label="Page 1 of 1",
                        )
                    )
            except Exception as e:
                logger.error(f"Failed to render Image {file_path}: {e}")
                raise ValueError(f"Invalid or corrupted image file: {e}")

        return pages_info

    @staticmethod
    def extract_digital_text_words(file_path: Path, dpi: int = 150) -> Dict[int, List[OCRWord]]:
        """
        Extracts digital vector words with coordinates from PDF pages if available.
        Coordinates are scaled to the rendered image pixel resolution (based on DPI).
        Returns mapping of page_num -> list of OCRWord.
        """
        page_words: Dict[int, List[OCRWord]] = {}
        if not PDFService.is_pdf(file_path):
            return page_words

        try:
            doc = fitz.open(str(file_path))
            scale = dpi / 72.0

            for page_idx in range(len(doc)):
                page_num = page_idx + 1
                page = doc[page_idx]
                words_raw = page.get_text("words")  # (x0, y0, x1, y1, word, block_no, line_no, word_no)
                
                words: List[OCRWord] = []
                for w in words_raw:
                    x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
                    if not text.strip():
                        continue
                    
                    # Convert to rendered pixel coordinates
                    px = x0 * scale
                    py = y0 * scale
                    pw = (x1 - x0) * scale
                    ph = (y1 - y0) * scale

                    words.append(
                        OCRWord(
                            text=text.strip(),
                            x=round(px, 2),
                            y=round(py, 2),
                            width=round(pw, 2),
                            height=round(ph, 2),
                            page=page_num,
                            confidence=1.0,
                        )
                    )
                page_words[page_num] = words
            doc.close()
        except Exception as e:
            logger.warning(f"Could not extract digital vector words from {file_path}: {e}")

        return page_words

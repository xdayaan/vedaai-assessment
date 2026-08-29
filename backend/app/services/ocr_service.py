import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image
import numpy as np

# 1. RapidOCR (pure Python / ONNX runtime)
try:
    from rapidocr_onnxruntime import RapidOCR
    _rapid_engine = RapidOCR()
    HAS_RAPIDOCR = True
except Exception:
    _rapid_engine = None
    HAS_RAPIDOCR = False

# 2. PyTesseract (fallback)
try:
    import pytesseract
    from pytesseract import Output
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False

from app.models.schemas import OCRWord, OCRLine, BoundingBox

logger = logging.getLogger("veda_ai.ocr_service")


class OCRService:
    @staticmethod
    def cluster_words_into_lines(
        words: List[OCRWord],
        page_num: int,
        line_height_tolerance_ratio: float = 0.6
    ) -> List[OCRLine]:
        """
        Groups words into structured lines based on vertical baseline alignment and left-to-right order.
        """
        if not words:
            return []

        # Sort words primarily top-to-bottom, secondarily left-to-right
        sorted_words = sorted(words, key=lambda w: (w.y, w.x))
        lines: List[List[OCRWord]] = []

        for word in sorted_words:
            matched = False
            word_center_y = word.y + (word.height / 2.0)

            for line in lines:
                # Compare with average center y of current line
                line_avg_center_y = sum(w.y + (w.height / 2.0) for w in line) / len(line)
                line_avg_height = sum(w.height for w in line) / len(line)
                tolerance = max(line_avg_height * line_height_tolerance_ratio, 8.0)

                if abs(word_center_y - line_avg_center_y) <= tolerance:
                    line.append(word)
                    matched = True
                    break

            if not matched:
                lines.append([word])

        ocr_lines: List[OCRLine] = []
        for line_words in lines:
            # Sort line words left-to-right
            line_words.sort(key=lambda w: w.x)

            min_x = min(w.x for w in line_words)
            min_y = min(w.y for w in line_words)
            max_x = max(w.x + w.width for w in line_words)
            max_y = max(w.y + w.height for w in line_words)

            line_text = " ".join(w.text for w in line_words).strip()
            if not line_text:
                continue

            ocr_lines.append(
                OCRLine(
                    text=line_text,
                    x=round(min_x, 2),
                    y=round(min_y, 2),
                    width=round(max_x - min_x, 2),
                    height=round(max_y - min_y, 2),
                    page=page_num,
                    words=line_words,
                )
            )

        # Sort lines top-to-bottom
        ocr_lines.sort(key=lambda l: (l.y, l.x))
        return ocr_lines

    @staticmethod
    def ocr_image_file(image_path: Path, page_num: int = 1) -> List[OCRWord]:
        """
        Runs OCR on an image file and extracts words with bounding box coordinates.
        Uses RapidOCR (ONNX) first, falls back to PyTesseract, and lastly OpenCV contour line segmentation.
        """
        words: List[OCRWord] = []

        # Option A: RapidOCR (high accuracy, ONNX model, pure Python)
        if HAS_RAPIDOCR and _rapid_engine:
            try:
                ocr_results, _ = _rapid_engine(str(image_path))
                if ocr_results:
                    for item in ocr_results:
                        box, text, score = item[0], item[1], float(item[2])
                        text_str = str(text).strip()
                        if not text_str:
                            continue

                        # box is [[x0,y0], [x1,y1], [x2,y2], [x3,y3]]
                        xs = [pt[0] for pt in box]
                        ys = [pt[1] for pt in box]
                        min_x, max_x = min(xs), max(xs)
                        min_y, max_y = min(ys), max(ys)

                        words.append(
                            OCRWord(
                                text=text_str,
                                x=round(min_x, 2),
                                y=round(min_y, 2),
                                width=round(max_x - min_x, 2),
                                height=round(max_y - min_y, 2),
                                page=page_num,
                                confidence=round(score, 3),
                            )
                        )
                    if words:
                        logger.info(f"RapidOCR extracted {len(words)} text regions on Page {page_num}")
                        return words
            except Exception as e:
                logger.warning(f"RapidOCR failed on {image_path}: {e}")

        # Option B: PyTesseract
        if HAS_PYTESSERACT:
            try:
                img = Image.open(str(image_path)).convert("RGB")
                data = pytesseract.image_to_data(img, output_type=Output.DICT)

                n_boxes = len(data["text"])
                for i in range(n_boxes):
                    text = data["text"][i].strip()
                    if not text:
                        continue

                    conf = float(data["conf"][i])
                    if conf < 0:
                        conf = 50.0

                    x = float(data["left"][i])
                    y = float(data["top"][i])
                    w = float(data["width"][i])
                    h = float(data["height"][i])

                    words.append(
                        OCRWord(
                            text=text,
                            x=round(x, 2),
                            y=round(y, 2),
                            width=round(w, 2),
                            height=round(h, 2),
                            page=page_num,
                            confidence=round(conf / 100.0, 3),
                        )
                    )
                if words:
                    logger.info(f"PyTesseract extracted {len(words)} words on Page {page_num}")
                    return words
            except Exception as e:
                logger.warning(f"PyTesseract OCR failed on {image_path}: {e}")

        return words

    @staticmethod
    def to_percentage_bbox(
        bbox: BoundingBox,
        page_width: float,
        page_height: float
    ) -> BoundingBox:
        """
        Converts pixel coordinates to 0-100 percentage coordinates.
        """
        if bbox.unit == "percentage":
            return bbox

        if page_width <= 0 or page_height <= 0:
            return bbox

        px = round((bbox.x / page_width) * 100.0, 2)
        py = round((bbox.y / page_height) * 100.0, 2)
        pw = round((bbox.width / page_width) * 100.0, 2)
        ph = round((bbox.height / page_height) * 100.0, 2)

        # Clamp values
        px = max(0.0, min(100.0, px))
        py = max(0.0, min(100.0, py))
        pw = max(0.1, min(100.0 - px, pw))
        ph = max(0.1, min(100.0 - py, ph))

        return BoundingBox(
            x=px,
            y=py,
            width=pw,
            height=ph,
            page=bbox.page,
            unit="percentage"
        )

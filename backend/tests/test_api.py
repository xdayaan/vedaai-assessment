import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.core.config import settings

client = TestClient(app)


def create_dummy_png_bytes(text="test"):
    img = Image.new("RGB", (600, 800), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def test_root_and_health():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

    resp_health = client.get("/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["status"] == "ok"


def test_upload_and_status_flow():
    qp_bytes = create_dummy_png_bytes("Question Paper")
    as_bytes = create_dummy_png_bytes("Answer Sheet")

    # 1. Upload files
    files = {
        "question_paper": ("qp.png", qp_bytes, "image/png"),
        "answer_sheet": ("as.png", as_bytes, "image/png"),
    }
    upload_resp = client.post("/api/assessments", files=files)
    assert upload_resp.status_code == 201
    data = upload_resp.json()
    assessment_id = data["assessment_id"]
    assert assessment_id.startswith("asm_")
    assert data["status"] == "uploaded"

    # 2. Check initial status
    status_resp = client.get(f"/api/assessments/{assessment_id}/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["stage"] == "uploaded"

    # 3. Start processing
    proc_resp = client.post(f"/api/assessments/{assessment_id}/process")
    assert proc_resp.status_code == 200
    assert proc_resp.json()["status"] == "processing"


def test_get_nonexistent_assessment():
    resp = client.get("/api/assessments/nonexistent_id")
    assert resp.status_code == 404

from __future__ import annotations
import io
from PIL import Image


def _create_png_bytes() -> bytes:
    img = Image.new("RGB", (32, 32), color=(120, 30, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def test_upload_success(client):
    payload = _create_png_bytes()

    response = client.post(
        "/api/images",
        files={"file": ("sample.png", payload, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"

    image_id = body["data"]["image_id"]
    detail = client.get(f"/api/images/{image_id}")
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["status"] == "success"
    assert detail_body["data"]["metadata"]["width"] == 32
    assert detail_body["data"]["thumbnails"]["small"].endswith("/small")

def test_invalid_file_type_rejected(client):
    response = client.post(
        "/api/images",
        files={"file": ("bad.gif", b"GIF89a", "image/gif")},
    )
    assert response.status_code == 400
    assert "JPG and PNG" in response.json()["detail"]

def test_stats_calculation(client):
    png_payload = _create_png_bytes()
    client.post("/api/images", files={"file": ("a.png", png_payload, "image/png")})
    client.post("/api/images", files={"file": ("b.gif", b"GIF89a", "image/gif")})

    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 2
    assert data["failed"] == 1
    assert data["success_rate"] == "50.00%"
    assert isinstance(data["average_processing_time_seconds"], float)



    
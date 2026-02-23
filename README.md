# Image Processing Pipeline (FastAPI + Pillow + SQLite + BLIP)

## Overview
This project is a complete local image-processing pipeline with:
- REST API for uploading and processing images.
- Simple web UI at `/` for non-technical users.
- Thumbnail generation (small + medium).
- Metadata extraction (dimensions, format, size, timestamp, optional EXIF).
- AI captioning using a HuggingFace BLIP model (loaded once on startup).
- SQLite persistence with processing status and timing metrics.

## Setup Instructions
Create venv and install requirement.txt:
1. Press Ctrl+Shift+P and search for Python: Select Interpreter
2. Click on + Create Virtual Environment
3. Select Venv
4. Select a python interpreter (Use Python 3.10+)
5. Select the requirements.txt and click OK
OR
6. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run server in command prompt
```bash
uvicorn app.main:app --reload
```
Server URL: `http://127.0.0.1:8000`

## Use the web UI
- Open: `http://127.0.0.1:8000/`
- Upload a JPG/PNG file.
- Wait for `Processing...`.
- View filename, caption, metadata, and two thumbnails.

Developer docs are available at: `http://127.0.0.1:8000/docs`

## API summary
- `POST /api/images` - upload JPG/PNG and process.
- `GET /api/images` - list image records + statuses.
- `GET /api/images/{id}` - detailed result payload.
- `GET /api/images/{id}/thumbnails/{small|medium}` - thumbnail bytes.
- `GET /api/stats` - aggregate processing stats.

## Example requests/responses
### Upload image
```bash
curl -X POST "http://127.0.0.1:8000/api/images" \
  -F "file=@/path/to/photo.jpg"
```

Example response:
```json
{
  "status": "success",
  "data": {
    "image_id": "img_ab12cd34ef56",
    "status": "success"
  },
  "error": null
}
```

### Fetch image detail
```bash
curl "http://127.0.0.1:8000/api/images/img_ab12cd34ef56"
```

Example response:
```json
{
  "status": "success",
  "data": {
    "image_id": "img_ab12cd34ef56",
    "original_name": "photo.jpg",
    "processed_at": "2026-01-01T12:00:00+00:00",
    "metadata": {
      "width": 1920,
      "height": 1080,
      "format": "jpeg",
      "size_bytes": 2048576
    },
    "thumbnails": {
      "small": "http://127.0.0.1:8000/api/images/img_ab12cd34ef56/thumbnails/small",
      "medium": "http://127.0.0.1:8000/api/images/img_ab12cd34ef56/thumbnails/medium"
    },
    "caption": "a scenic landscape with mountains"
  },
  "error": null
}
```

### List images
```bash
curl "http://127.0.0.1:8000/api/images"
```

### Get stats
```bash
curl "http://127.0.0.1:8000/api/stats"
```

## Processing pipeline notes
1. API receives upload and creates a DB row with `processing` status.
2. File type is validated (JPG/PNG only).
3. Original image is saved to disk.
4. Pillow extracts dimensions/format/size (+ EXIF if present).
5. Two thumbnails are created and saved.
6. BLIP caption is generated (fallback to `Caption unavailable` if model fails).
7. DB row updates to `success` or `failed` with processing time and error details.

## Testing
Run:
```bash
pytest
```

# LightOnOCR Service

FastAPI + RQ + Redis service that runs OCR on PDFs and images using the
LightOnOCR-2-1B vision-language model. Jobs are queued, processed by workers,
and results are returned as structured JSON that can be converted to Markdown.

## Features
- Upload a PDF or image and queue OCR in Redis
- Background workers run the model and return per-page text
- Simple status endpoint for job polling
- Utility CLI to convert OCR JSON output to Markdown

## API
- `POST /process_file` (multipart file upload)
- `GET /jobs/{job_id}`
- `GET /health`

Example:
```bash
curl -X POST "http://localhost:8000/process_file" -F "file=@sample.pdf"
```

## Run Locally
1. Install dependencies:
```bash
pip install -r requirements.txt
```
1. Set environment variables (see `.env.example`).
1. Start Redis (local or Docker).
1. Start the API:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
1. Start a worker:
```bash
cd app
rq worker OCR_TASK_QUEUE
```

## Docker
```bash
docker-compose up --build
```



## JSON to Markdown Utility
Convert OCR JSON output to Markdown:
```bash
python -m app.utils.ocr_to_md path/to/ocr.json
```

Write to a specific file:
```bash
python -m app.utils.ocr_to_md path/to/ocr.json -o output.md
```

## Environment Variables
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_QUEUE_NAME`
- `HF_TOKEN` (optional, for Hugging Face access)

## Model Attribution
This project uses the LightOnOCR-2-1B model from Hugging Face, which is
described as a flagship OCR model and is licensed under Apache-2.0. The model
card and details are available on Hugging Face.

[Hugging Face model page](https://huggingface.co/lightonai/LightOnOCR-2-1B)


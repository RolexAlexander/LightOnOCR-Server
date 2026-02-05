import os
from fastapi import FastAPI
from fastapi import UploadFile
from dotenv import load_dotenv

from rq import Queue, Retry
from rq.job import Job, NoSuchJobError
from app.redis_conn import redis_conn
from app.tasks.ocr import process_ocr


# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI()

# Create redis queue
ocr_queue = Queue(os.getenv("REDIS_QUEUE_NAME"), connection=redis_conn)


# OCR endpoint
@app.post("/process_file")
def process_file(file: UploadFile):
    """"""
    # Create job in the queue
    job = ocr_queue.enqueue(
        process_ocr,
        file.file.read(),
        retry=Retry(max=3, interval=[10, 30, 60]),
        result_ttl=86400,
        job_timeout=1000
    )
    
    # Return job ID
    return {"job_id": job.id}


# Job status endpoint
@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except NoSuchJobError:
        return {
            "status": "not_found",
            "result": None
        }

    return {
        "status": job.get_status(),
        "result": job.result if job.is_finished else None
    }

    
# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

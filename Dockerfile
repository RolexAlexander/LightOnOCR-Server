FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install uvicorn and other dependencies
RUN pip install --no-cache-dir "uvicorn[standard]"

COPY app/ app/

ENV PYTHONUNBUFFERED=1

# default command (can be overridden)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

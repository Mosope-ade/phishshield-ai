FROM python:3.11-slim

# Install system dependencies for QR decoding (libzbar0) and OCR Fallback (tesseract-ocr)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libzbar0 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend codebase
COPY backend/ /app/backend

# Expose container port
EXPOSE 8000

# Bind host to 0.0.0.0 so that the container is reachable externally
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

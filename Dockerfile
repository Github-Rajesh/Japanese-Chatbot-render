FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    nginx \
    tesseract-ocr \
    tesseract-ocr-jpn \
    tesseract-ocr-jpn-vert \
    poppler-utils \
    libmagic1 \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ /usr/share/nginx/html/

# Copy nginx config
COPY nginx-render.conf /etc/nginx/sites-available/default

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create directories
RUN mkdir -p "knowledge base main/uploads" "data/vectorstore"

# Expose port (Render uses PORT environment variable)
EXPOSE 10000

# Start supervisor (runs both nginx and backend)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
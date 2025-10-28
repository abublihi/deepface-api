FROM python:3.10-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser gunicorn_conf.py .

# Switch to non-root user
USER appuser

# Create directory for DeepFace models
RUN mkdir -p /home/appuser/.deepface/weights

# Preload models to reduce cold start time
RUN python -c "import os; os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'; \
    from deepface import DeepFace; \
    import numpy as np; \
    dummy_img = np.zeros((224, 224, 3), dtype=np.uint8); \
    print('Preloading SFace model...'); \
    DeepFace.represent(dummy_img, model_name='SFace', enforce_detection=False); \
    print('Preloading analysis models...'); \
    DeepFace.analyze(dummy_img, actions=['age', 'gender', 'race', 'emotion'], enforce_detection=False, silent=True); \
    print('All models preloaded successfully!')"

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Launch with Gunicorn using Uvicorn workers
CMD ["gunicorn", \
    "-c", "gunicorn_conf.py", \
    "-k", "uvicorn.workers.UvicornWorker", \
    "app.main:app", \
    "--bind", "0.0.0.0:8000"]

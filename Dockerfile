# ──────────────────────────────────────────────────────────────────────────────
# NeuroScan AI — Dockerfile
# Made by Mohammed Mourad Abdelhafidi
# ──────────────────────────────────────────────────────────────────────────────
# Uses CPU-only PyTorch to keep the image lean (~1.5 GB vs 5+ GB with CUDA).
# The HuggingFace model is downloaded at first launch and cached inside the
# container volume.
# ──────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# Install system dependencies for Pillow / image handling
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libjpeg62-turbo-dev \
        libpng-dev \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for Docker layer caching
COPY requirements.txt .

# Install CPU-only PyTorch first (saves ~3 GB vs the default CUDA bundle),
# then install the rest of the requirements
RUN pip install --no-cache-dir \
        torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create the data directory for SQLite + saved images
RUN mkdir -p data/images

# Expose the Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the app
CMD ["streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true"]

# 🧠 NeuroScan AI

> **Made by Mohammed Mourad Abdelhafidi**

MRI-based brain tumor classification powered by a fine-tuned SigLIP vision transformer — wrapped in a clinical-themed Streamlit interface with scan history, search, and PDF report export.

> **⚠️ PoC Disclaimer**
> This application is a technical **Proof of Concept** built for research and demonstration purposes only. It is **not intended for clinical diagnostic use**. Model accuracy is experimental and has not been validated against clinical benchmarks. Always consult a qualified medical professional for diagnosis.

---

## Features

- **Upload & Classify** — Drag-and-drop an MRI scan (JPG/PNG) to get an instant 4-class prediction
- **Confidence Breakdown** — Full probability distribution across all classes with color-coded visualization
- **Save & Name Scans** — Persist results with a custom label (patient ID, description, etc.)
- **Scan History** — Browse all saved scans with expandable detail cards
- **Search** — Filter saved scans by name
- **PDF Export** — Download a formatted diagnostic report for any saved scan
- **Delete** — Remove individual scans and their associated image files

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | [Streamlit](https://streamlit.io/) |
| ML Framework | [PyTorch](https://pytorch.org/) |
| Model Inference | [HuggingFace Transformers](https://huggingface.co/docs/transformers) |
| Database | SQLite (via Python `sqlite3`) |
| PDF Generation | [fpdf2](https://github.com/py-pdf/fpdf2) |

---

## Model

This app uses [**prithivMLmods/BrainTumor-Classification-Mini**](https://huggingface.co/prithivMLmods/BrainTumor-Classification-Mini), a SigLIP-based image classifier fine-tuned on brain MRI data.

**Classes:** `Glioma`, `Meningioma`, `Pituitary`, `No Tumor`

> **Note:** Model accuracy is experimental and unverified for clinical use. This is a demonstration of ML-powered medical image classification, not a diagnostic tool.

---

## Local Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/brain-tumor-classifier.git
cd brain-tumor-classifier

# Create and activate a virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install PyTorch (CPU-only — saves ~3 GB)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Deployment Guide

### Handling the 2.5 GB+ File Size

The large file size comes from `venv/` (Python packages + PyTorch) and the HuggingFace model cache. Here's how to handle it:

- **`venv/` is in `.gitignore`** — it is never pushed to Git. The cloud platform rebuilds dependencies from `requirements.txt`.
- **The HuggingFace model** (~200 MB) is downloaded automatically on first launch and cached in `~/.cache/huggingface/`.
- **Use CPU-only PyTorch** to reduce install size from ~5 GB to ~1.5 GB.
- **For large binary files** (e.g., benchmark images), use [Git LFS](https://git-lfs.github.com/):
  ```bash
  git lfs install
  git lfs track "*.jpg"
  ```

---

### Option A: Docker Deployment (Recommended)

The included `Dockerfile` uses CPU-only PyTorch and produces a lean ~1.5 GB image.

```bash
# Build the image
docker build -t neuroscan-ai .

# Run the container
docker run -p 8501:8501 neuroscan-ai

# Persist scan history across restarts
docker run -p 8501:8501 -v neuroscan_data:/app/data neuroscan-ai
```

Visit `http://localhost:8501` to use the app.

---

### Option B: Render.com (Free Tier Available)

1. **Push your code to GitHub** (the `venv/` folder is excluded by `.gitignore`)
2. **Go to [render.com](https://render.com)** → New → Web Service
3. **Connect your GitHub repository**
4. Render auto-detects the `Dockerfile` and builds from it
5. **Click "Create Web Service"** — your app deploys at `https://your-app.onrender.com`

**Without Docker (native runtime):**
- **Build Command:** `pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements.txt`
- **Start Command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

---

### Option C: Streamlit Community Cloud

1. Push to GitHub (public repository)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" → select your repository → set `app.py` as the main file
4. Add a `packages.txt` with system dependencies if needed

> **Note:** Streamlit Community Cloud has resource limits. For models this size, Docker-based deployment (Options A or B) is more reliable.

---

### Option D: Railway

1. Push to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Railway auto-detects the `Dockerfile` or `Procfile`
4. Your app deploys automatically

---

## Generating the Showcase PDF

```bash
python generate_showcase_pdf.py
```

This produces `NeuroScan_AI_Showcase.pdf` — a multi-page document with the project story, technical breakdown, and deployment guide.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  <b>Made with ❤️ by Mohammed Mourad Abdelhafidi</b>
</p>

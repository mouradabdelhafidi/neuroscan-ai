# 🧠 NeuroScan AI

> **Made by Mohammed Mourad Abdelhafidi**

MRI-based brain tumor classification powered by a fine-tuned SigLIP vision transformer — wrapped in a clinical-themed Streamlit interface with scan history, search, and PDF report export.

> **⚠️ PoC Disclaimer**
> This application is a technical **Proof of Concept** built for research and demonstration purposes only. It is **not intended for clinical diagnostic use**. Model accuracy is experimental and has not been validated against clinical benchmarks. Always consult a qualified medical professional for diagnosis.

> **🚀 Live Demo**: [https://neuroscan-ai-tech.streamlit.app/](https://neuroscan-ai-tech.streamlit.app/)

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

The app will open locally at `http://localhost:8501`.

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

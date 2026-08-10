# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import torch
from transformers import AutoImageProcessor, SiglipForImageClassification
from PIL import Image
import torch.nn.functional as F
import json
import db
from fpdf import FPDF
from datetime import datetime
import os

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="NeuroScan AI | MRI Classification",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── UI STYLING ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #0a0c10 !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 8px !important;
    padding: 2rem !important;
}

/* Diagnostic viewfinder for image */
div[data-testid="stImage"] {
    padding: 10px;
    background: 
        linear-gradient(to right, #22d3ee 2px, transparent 2px) 0 0,
        linear-gradient(to bottom, #22d3ee 2px, transparent 2px) 0 0,
        linear-gradient(to left, #22d3ee 2px, transparent 2px) 100% 0,
        linear-gradient(to bottom, #22d3ee 2px, transparent 2px) 100% 0,
        linear-gradient(to right, #22d3ee 2px, transparent 2px) 0 100%,
        linear-gradient(to top, #22d3ee 2px, transparent 2px) 0 100%,
        linear-gradient(to left, #22d3ee 2px, transparent 2px) 100% 100%,
        linear-gradient(to top, #22d3ee 2px, transparent 2px) 100% 100%;
    background-repeat: no-repeat;
    background-size: 20px 20px;
}

.footer-banner {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: #0a0c10;
    border-top: 1px solid rgba(251, 191, 36, 0.5);
    color: #fbbf24;
    text-align: center;
    padding: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    z-index: 99999;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Custom styles for monospace readout */
.mono-readout {
    font-family: 'JetBrains Mono', monospace;
}
.mono-label {
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #9ca3af;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────────────────────────

st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1f2937; padding-bottom: 10px; margin-bottom: 30px;">
    <div style="margin: 0; font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; color: #E5E7EB; font-weight: bold;">🧠 NeuroScan AI</div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); padding: 4px 8px; border-radius: 4px; background: rgba(251, 191, 36, 0.05);">PoC — Not for clinical use</div>
</div>
""", unsafe_allow_html=True)

# ── MODEL ────────────────────────────────────────────────────────────────────

MODEL_NAME = "prithivMLmods/BrainTumor-Classification-Mini"

@st.cache_resource(show_spinner="Initializing Model...")
def load_model():
    """Load the image processor and SigLIP classification model from HuggingFace."""
    processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
    model = SiglipForImageClassification.from_pretrained(MODEL_NAME)
    return processor, model

processor, model = load_model()

# ── DATABASE ─────────────────────────────────────────────────────────────────

db.init_db()

# ── LABEL METADATA ───────────────────────────────────────────────────────────

CLASS_INFO = {
    "glioma": "Gliomas are tumors that develop from glial cells in the brain or spinal cord. They can be benign or malignant.",
    "meningioma": "Meningiomas are typically slow-growing tumors that form on the meninges, the protective layers covering the brain and spinal cord. Most are benign.",
    "pituitary": "Pituitary tumors develop in the pituitary gland at the base of the brain. They are generally benign but can affect hormone production.",
    "notumor": "No signs of a brain tumor detected in the current scan. (Note: This is a PoC prediction only.)"
}

COLOR_MAP = {
    "glioma": "#cc5555",      # muted red
    "meningioma": "#d9822b",  # muted orange
    "pituitary": "#8b5cf6",   # muted violet
    "notumor": "#4ade80"      # muted green
}

# ── PREDICTION LOGIC ─────────────────────────────────────────────────────────

def predict(image):
    """Run inference on a PIL image and return the predicted class and all probabilities."""
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits
    probabilities = F.softmax(logits, dim=-1).squeeze().tolist()
    
    class_names = [model.config.id2label[i] for i in range(len(model.config.id2label))]
    
    results = {class_names[i]: probabilities[i] for i in range(len(class_names))}
    predicted_class = max(results, key=results.get)
    
    return predicted_class, results

def get_class_key(cls_name):
    """Normalize a model label string to a canonical key for CLASS_INFO / COLOR_MAP lookup."""
    class_key = cls_name.lower()
    if "glioma" in class_key: return "glioma"
    if "meningioma" in class_key: return "meningioma"
    if "pituitary" in class_key: return "pituitary"
    if "no" in class_key and "tumor" in class_key: return "notumor"
    return "notumor"

# ── ANALYZE TAB ──────────────────────────────────────────────────────────────

tab_analyze, tab_history = st.tabs(["Analyze", "History"])

with tab_analyze:
    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            st.markdown("<div class='mono-label' style='margin-bottom:10px;'>[ INPUT : UPLOAD_MRI ]</div>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Select scan file...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file).convert('RGB')
                st.image(image, use_column_width=True)

    with col2:
        with st.container(border=True):
            st.markdown("<div class='mono-label' style='margin-bottom:10px;'>[ OUTPUT : ANALYSIS_RESULTS ]</div>", unsafe_allow_html=True)
        
        if uploaded_file is not None:
            with st.spinner("Processing..."):
                predicted_class, results = predict(image)
                class_key = get_class_key(predicted_class)
                
                # Top Prediction area
                st.markdown(f"<div style='margin-bottom: 20px;'><div class='mono-label'>Primary Detection</div><div style=\"font-family: 'JetBrains Mono', monospace; letter-spacing: 1px; font-size: 2.2rem; font-weight: bold; color: #E5E7EB; line-height: 1.2; margin-bottom: 15px; text-transform: uppercase;\">{predicted_class}</div><div class='mono-label'>Confidence Score</div><div class='mono-readout' style='font-size: 1.8rem; color: #22d3ee; line-height: 1;'>{results[predicted_class]*100:.2f}%</div><div style='width: 100%; height: 2px; background: #1f2937; margin-top: 8px;'><div style='width: {results[predicted_class]*100}%; height: 100%; background: #22d3ee;'></div></div></div>", unsafe_allow_html=True)
                
                st.markdown(f"<div style='font-size:0.9rem; color:#9ca3af; margin-bottom: 25px; border-left: 2px solid #374151; padding-left: 10px;'>{CLASS_INFO.get(class_key, '')}</div>", unsafe_allow_html=True)
                
                # 4-class breakdown
                st.markdown("<div class='mono-label' style='margin-bottom: 15px;'>Probabilities Breakdown</div>", unsafe_allow_html=True)
                
                breakdown_html = "<div style='display: flex; flex-direction: column; gap: 10px;'>"
                for cls_name, prob in sorted(results.items(), key=lambda x: x[1], reverse=True):
                    c_key = get_class_key(cls_name)
                    c_color = COLOR_MAP.get(c_key, "#6b7280")
                    breakdown_html += f"<div style=\"display: flex; justify-content: space-between; align-items: center; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;\"><div style='display: flex; align-items: center;'><span style='display: inline-block; width: 12px; height: 12px; background-color: {c_color}; margin-right: 10px; border-radius: 2px;'></span><span style='color: #d1d5db; text-transform: uppercase;'>{cls_name}</span></div><span style='color: #9ca3af;'>{prob*100:.1f}%</span></div>"
                breakdown_html += "</div>"
                
                st.markdown(breakdown_html, unsafe_allow_html=True)
                
                st.markdown("<div style='font-family: \"JetBrains Mono\", monospace; font-size: 0.75rem; color: #fbbf24; margin-top: 25px; border-top: 1px dashed #374151; padding-top: 10px;'>[CAVEAT] Model accuracy is experimental — verify against multiple scans.</div>", unsafe_allow_html=True)
                
                # Save to History UI
                st.markdown("<div style='margin-top: 25px; border-top: 1px solid #374151; padding-top: 15px;'></div>", unsafe_allow_html=True)
                scan_name = st.text_input("Name this scan", placeholder="Optional: Patient ID or description", key="scan_name_input")
                
                if st.button("Save to History", use_container_width=True, type="primary"):
                    final_name = scan_name.strip() if scan_name.strip() else f"Scan - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    try:
                        db.save_scan(final_name, image, predicted_class, results[predicted_class], results)
                        st.toast("Scan saved successfully!", icon="✅")
                    except Exception as e:
                        st.error(f"Error saving scan: {e}")
                
        else:
            st.markdown("<div style='color: #4b5563; font-family: \"JetBrains Mono\", monospace; font-size: 0.9rem; margin-top: 20px;'>Waiting for input data...</div>", unsafe_allow_html=True)

# ── HISTORY TAB ──────────────────────────────────────────────────────────────

with tab_history:
    st.markdown("<div class='mono-label' style='margin-bottom:10px;'>[ SAVED SCANS ]</div>", unsafe_allow_html=True)
    search_query = st.text_input("Search by name...", key="history_search")
    
    scans = db.search_scans_by_name(search_query) if search_query else db.get_all_scans()
    
    if not scans:
        st.markdown("<div style='color: #4b5563; font-family: \"JetBrains Mono\", monospace; font-size: 0.9rem; margin-top: 20px;'>No saved scans found.</div>", unsafe_allow_html=True)
    else:
        for scan in scans:
            with st.expander(f"📁 {scan['name']} | 🤖 {scan['prediction'].upper()} ({scan['confidence']*100:.1f}%) | 🕒 {scan['created_at'][:19]}"):
                h_col1, h_col2 = st.columns([1, 2], gap="large")
                with h_col1:
                    if os.path.exists(scan['image_path']):
                        try:
                            st.image(Image.open(scan['image_path']), use_column_width=True)
                        except Exception:
                            st.error("Image file corrupted")
                    else:
                        st.error("Image file missing")
                        
                with h_col2:
                    st.markdown("<div class='mono-label' style='margin-bottom: 10px;'>Probabilities Breakdown</div>", unsafe_allow_html=True)
                    probs = json.loads(scan['all_probabilities'])
                    breakdown_html = "<div style='display: flex; flex-direction: column; gap: 8px;'>"
                    for cls_name, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
                        c_key = get_class_key(cls_name)
                        c_color = COLOR_MAP.get(c_key, "#6b7280")
                        breakdown_html += f"<div style=\"display: flex; justify-content: space-between; align-items: center; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;\"><div style='display: flex; align-items: center;'><span style='display: inline-block; width: 12px; height: 12px; background-color: {c_color}; margin-right: 10px; border-radius: 2px;'></span><span style='color: #d1d5db; text-transform: uppercase;'>{cls_name}</span></div><span style='color: #9ca3af;'>{prob*100:.1f}%</span></div>"
                    breakdown_html += "</div>"
                    st.markdown(breakdown_html, unsafe_allow_html=True)
                    
                    st.markdown("<hr style='border-color: #374151; margin: 15px 0;'>", unsafe_allow_html=True)
                    
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("Delete Scan", key=f"del_{scan['id']}", type="secondary"):
                            db.delete_scan(scan['id'])
                            st.rerun()
                    with btn_col2:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("helvetica", "B", 16)
                        pdf.cell(0, 10, f"NeuroScan AI Report: {scan['name']}", ln=True, align="C")
                        pdf.set_font("helvetica", "I", 9)
                        pdf.cell(0, 6, "Made by Mohammed Mourad Abdelhafidi", ln=True, align="C")
                        pdf.ln(5)
                        
                        pdf.set_font("helvetica", size=12)
                        pdf.cell(0, 8, f"Date: {scan['created_at'][:19]}", ln=True)
                        pdf.cell(0, 8, f"Prediction: {scan['prediction'].upper()}", ln=True)
                        pdf.cell(0, 8, f"Confidence: {scan['confidence']*100:.1f}%", ln=True)
                        pdf.ln(5)
                        
                        if os.path.exists(scan['image_path']):
                            try:
                                pdf.image(scan['image_path'], w=100)
                                pdf.ln(5)
                            except Exception:
                                pass
                                
                        pdf.set_font("helvetica", "B", 12)
                        pdf.cell(0, 8, "Probabilities Breakdown:", ln=True)
                        pdf.set_font("helvetica", size=10)
                        for cls_name, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
                            pdf.cell(0, 6, f"- {cls_name.upper()}: {prob*100:.1f}%", ln=True)
                            
                        pdf.ln(10)
                        pdf.set_font("helvetica", "I", 8)
                        pdf.multi_cell(0, 5, "Medical Disclaimer: This application is a technical Proof of Concept (PoC) built for research/demonstration purposes only and is not intended for clinical diagnostic use.")
                        
                        pdf_bytes = bytes(pdf.output())
                        
                        st.download_button(
                            label="Export PDF",
                            data=pdf_bytes,
                            file_name=f"neuroscan_{scan['id']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{scan['id']}"
                        )

# ── FOOTER ───────────────────────────────────────────────────────────────────

st.markdown('<div class="footer-banner">⚠️ Medical Disclaimer: PoC only — not for clinical use. &nbsp;|&nbsp; Made by Mohammed Mourad Abdelhafidi</div>', unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

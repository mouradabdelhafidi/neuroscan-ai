"""Generate a multi-page showcase PDF for NeuroScan AI.

This script produces a professional, emotionally compelling PDF that tells the
story of why this project was built, what it does, how it works, and step-by-step
deployment instructions -- perfect for portfolios, presentations, or sharing.

Made by Mohammed Mourad Abdelhafidi
"""

import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos


# ── CUSTOM PDF CLASS ─────────────────────────────────────────────────────────

class ShowcasePDF(FPDF):
    """A branded PDF with header/footer, consistent colors, and helper methods."""

    # Brand colors
    DARK_BG = (10, 12, 16)
    CYAN = (34, 211, 238)
    GOLD = (251, 191, 36)
    WHITE = (229, 231, 235)
    GRAY = (156, 163, 175)

    def header(self):
        if self.page_no() == 1:
            return  # Cover page has its own header
        self.set_font("helvetica", "I", 8)
        self.set_text_color(*self.GRAY)
        self.cell(0, 8, "NeuroScan AI  |  Made by Mohammed Mourad Abdelhafidi", align="L")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(*self.GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def section_title(self, title):
        self.set_font("helvetica", "B", 18)
        self.set_text_color(34, 211, 238)
        self.cell(0, 12, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Underline
        self.set_draw_color(*self.CYAN)
        self.set_line_width(0.5)
        y = self.get_y()
        self.line(10, y, 200, y)
        self.ln(6)

    def body_text(self, text):
        self.set_font("helvetica", "", 11)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 7, text)
        self.ln(3)

    def quote_text(self, text):
        """Render an indented, italicized quote block."""
        self.set_font("helvetica", "I", 11)
        self.set_text_color(100, 100, 100)
        x = self.get_x()
        self.set_x(x + 8)
        # Draw a thin left border
        y_start = self.get_y()
        self.multi_cell(170, 7, text)
        y_end = self.get_y()
        self.set_draw_color(*self.GOLD)
        self.set_line_width(1.0)
        self.line(x + 4, y_start, x + 4, y_end)
        self.ln(4)

    def bullet(self, text):
        self.set_font("helvetica", "", 11)
        self.set_text_color(60, 60, 60)
        x = self.get_x()
        self.set_x(x + 6)
        # Bullet character
        self.set_font("zapfdingbats", "", 7)
        self.set_text_color(*self.CYAN)
        self.cell(5, 7, "l")  # small filled circle in ZapfDingbats
        self.set_font("helvetica", "", 11)
        self.set_text_color(60, 60, 60)
        self.multi_cell(170, 7, text)
        self.ln(1)

    def step_item(self, number, title, details):
        """Render a numbered step with a bold title and detail text."""
        self.set_font("helvetica", "B", 12)
        self.set_text_color(*self.CYAN)
        self.cell(10, 8, f"{number}.")
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("helvetica", "", 10)
        self.set_text_color(80, 80, 80)
        self.set_x(self.get_x() + 12)
        self.multi_cell(170, 6, details)
        self.ln(3)

    def code_block(self, code):
        """Render monospaced code in a light-gray box."""
        self.set_fill_color(240, 240, 240)
        self.set_font("courier", "", 9)
        self.set_text_color(30, 30, 30)
        x = self.get_x()
        self.set_x(x + 6)
        self.multi_cell(178, 5, code, fill=True)
        self.ln(3)


# ── BUILD THE PDF ────────────────────────────────────────────────────────────

def build_showcase_pdf():
    pdf = ShowcasePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ╔════════════════════════════════════════════════════════════════════════╗
    # ║  PAGE 1 -- COVER                                                       ║
    # ╚════════════════════════════════════════════════════════════════════════╝

    pdf.add_page()

    pdf.ln(50)
    pdf.set_font("helvetica", "B", 36)
    pdf.set_text_color(34, 211, 238)
    pdf.cell(0, 16, "NeuroScan AI", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("helvetica", "", 14)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 10, "Brain Tumor MRI Classification", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, "Powered by Deep Learning", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(20)

    # Divider line
    pdf.set_draw_color(251, 191, 36)
    pdf.set_line_width(0.8)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(15)

    pdf.set_font("helvetica", "I", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "A Proof-of-Concept at the Intersection of AI and Healthcare",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(40)

    pdf.set_font("helvetica", "B", 13)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, "Made by Mohammed Mourad Abdelhafidi", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 8, "2026", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ╔════════════════════════════════════════════════════════════════════════╗
    # ║  PAGE 2 -- THE STORY                                                    ║
    # ╚════════════════════════════════════════════════════════════════════════╝

    pdf.add_page()
    pdf.section_title("The Story Behind NeuroScan AI")

    pdf.quote_text(
        '"In a hospital hallway somewhere in the world, a family sits waiting. '
        'The fluorescent lights hum above them. A child sleeps in his mother\'s '
        'arms, unaware that inside his small skull, something uninvited has begun '
        'to grow. The MRI is done. Now they wait."'
    )

    pdf.body_text(
        "Brain tumors are among the most devastating diagnoses a family can face. "
        "Every year, over 300,000 people worldwide are diagnosed with a brain or "
        "central nervous system tumor. For many of them, early and accurate "
        "classification of the tumor type is the difference between life and death, "
        "between a targeted treatment plan and months of uncertainty."
    )

    pdf.body_text(
        "But here is the heartbreaking reality: in many parts of the world, "
        "neuroradiologists are scarce. Rural hospitals, underfunded clinics, and "
        "developing nations often lack the specialized expertise to quickly classify "
        "what an MRI reveals. A scan sits on a screen. A doctor, trained in general "
        "medicine but not in the subtle gradations of glioma versus meningioma, "
        "stares at it and does their best. Precious hours pass. Sometimes days."
    )

    pdf.body_text(
        "I built NeuroScan AI because I believe technology should be a bridge, "
        "not a barrier. I believe that a single developer with a laptop, a deep "
        "learning model, and a refusal to accept the status quo can build something "
        "that points the way toward a future where no family waits longer than they "
        "have to."
    )

    pdf.quote_text(
        '"This project is not a clinical tool. It is a proof of concept. But every '
        'revolution begins with a proof of concept. Every bridge begins with '
        'someone who looked at the gap and said: I can build something."'
    )

    pdf.body_text(
        "NeuroScan AI is my answer to that gap. It is my way of saying that "
        "artificial intelligence belongs not just in the hands of giant corporations, "
        "but in the hands of anyone who cares enough to build, to learn, and to try. "
        "It is a small light, but in the darkness of a diagnosis, even a small light "
        "matters."
    )

    pdf.ln(5)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(251, 191, 36)
    pdf.cell(0, 8, "-- Mohammed Mourad Abdelhafidi", align="R",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ╔════════════════════════════════════════════════════════════════════════╗
    # ║  PAGE 3 -- WHAT IT DOES                                                 ║
    # ╚════════════════════════════════════════════════════════════════════════╝

    pdf.add_page()
    pdf.section_title("What NeuroScan AI Does")

    pdf.body_text(
        "NeuroScan AI is a web application that classifies brain MRI scans into "
        "four categories using a fine-tuned SigLIP vision transformer model:"
    )

    pdf.ln(3)
    pdf.bullet("Glioma -- Tumors from glial cells; can be benign or malignant")
    pdf.bullet("Meningioma -- Slow-growing tumors on the brain's protective layers")
    pdf.bullet("Pituitary -- Tumors in the pituitary gland affecting hormones")
    pdf.bullet("No Tumor -- No signs of a brain tumor detected")

    pdf.ln(3)
    pdf.body_text("Key features of the application:")
    pdf.bullet("Drag-and-drop MRI upload with instant classification")
    pdf.bullet("Full confidence breakdown across all four classes with color-coded visualization")
    pdf.bullet("Save and name scans with custom labels (patient ID, description)")
    pdf.bullet("Browse scan history with expandable detail cards and search")
    pdf.bullet("Export professional PDF diagnostic reports for any saved scan")
    pdf.bullet("Delete individual scans and their associated files")

    # ╔════════════════════════════════════════════════════════════════════════╗
    # ║  PAGE 4 -- HOW IT WORKS                                                ║
    # ╚════════════════════════════════════════════════════════════════════════╝

    pdf.add_page()
    pdf.section_title("How It Works -- Under the Hood")

    pdf.body_text(
        "The application is built on a modern, layered architecture that separates "
        "concerns cleanly between the user interface, machine learning inference, "
        "data persistence, and report generation."
    )

    pdf.ln(2)
    pdf.set_font("helvetica", "B", 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, "Architecture", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.body_text(
        "1. Frontend (Streamlit): A clinical-themed dark interface with custom CSS, "
        "JetBrains Mono typography, and diagnostic viewfinder styling for MRI images.\n\n"
        "2. ML Inference (PyTorch + HuggingFace Transformers): The SigLIP-based model "
        "'BrainTumor-Classification-Mini' processes images through an AutoImageProcessor, "
        "runs inference with torch.no_grad(), and produces softmax probabilities.\n\n"
        "3. Database (SQLite): Scan records (ID, name, image path, prediction, confidence, "
        "full probability JSON, timestamp) are persisted locally using Python's built-in "
        "sqlite3 module.\n\n"
        "4. PDF Reports (fpdf2): Professional diagnostic reports are generated on-demand "
        "with embedded MRI images, probability breakdowns, and medical disclaimers."
    )

    pdf.ln(3)
    pdf.set_font("helvetica", "B", 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, "Technical Stack", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Table
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(34, 211, 238)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 8, "Layer", fill=True, border=1)
    pdf.cell(120, 8, "Technology", fill=True, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    rows = [
        ("Frontend", "Streamlit (Python)"),
        ("ML Framework", "PyTorch"),
        ("Model Inference", "HuggingFace Transformers (SigLIP)"),
        ("Image Processing", "Pillow (PIL)"),
        ("Database", "SQLite (sqlite3)"),
        ("PDF Generation", "fpdf2"),
        ("Benchmarking", "Custom script + pyarrow + datasets"),
    ]
    pdf.set_font("helvetica", "", 10)
    for i, (layer, tech) in enumerate(rows):
        fill = i % 2 == 0
        if fill:
            pdf.set_fill_color(240, 248, 255)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(60, 7, layer, fill=fill, border=1)
        pdf.cell(120, 7, tech, fill=fill, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)



    # ╔════════════════════════════════════════════════════════════════════════╗
    # ║  PAGE 6 -- CLOSING                                                      ║
    # ╚════════════════════════════════════════════════════════════════════════╝

    pdf.add_page()
    pdf.section_title("A Final Word")

    pdf.quote_text(
        '"Every great technology was once a small idea in someone\'s mind. '
        'Every life saved by medicine was once a problem someone refused to ignore. '
        'NeuroScan AI is not the end -- it is a beginning."'
    )

    pdf.body_text(
        "This project was built with the conviction that artificial intelligence, "
        "when guided by compassion and purpose, has the power to transform "
        "healthcare. Not tomorrow. Not in some distant future. But now -- one "
        "proof of concept at a time."
    )

    pdf.body_text(
        "To every student, self-taught developer, and dreamer reading this: "
        "you do not need a laboratory or a research grant to make a difference. "
        "You need curiosity, persistence, and the courage to build something "
        "that matters. The tools are free. The knowledge is open. The only "
        "missing ingredient is you."
    )

    pdf.body_text(
        "If this project helps even one person understand how AI can assist in "
        "medical imaging -- if it inspires even one more developer to build "
        "something at the intersection of technology and human health -- then "
        "it has already succeeded far beyond what any accuracy metric could measure."
    )

    pdf.ln(10)
    pdf.set_draw_color(251, 191, 36)
    pdf.set_line_width(0.8)
    y = pdf.get_y()
    pdf.line(60, y, 150, y)
    pdf.ln(10)

    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(34, 211, 238)
    pdf.cell(0, 10, "Made by Mohammed Mourad Abdelhafidi", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 8, "NeuroScan AI  |  2026", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── DISCLAIMER ───────────────────────────────────────────────────────────

    pdf.ln(15)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 4,
        "DISCLAIMER: NeuroScan AI is a technical Proof of Concept (PoC) built for "
        "research and demonstration purposes only. It is not intended for clinical "
        "diagnostic use. Model accuracy is experimental and has not been validated "
        "against clinical benchmarks. Always consult a qualified medical professional "
        "for diagnosis and treatment decisions."
    )

    # ── SAVE ─────────────────────────────────────────────────────────────────

    output_path = os.path.join(os.path.dirname(__file__), "NeuroScan_AI_Showcase.pdf")
    pdf.output(output_path)
    print(f"\nShowcase PDF generated successfully!")
    print(f"  -> {output_path}")
    print(f"  -> {pdf.page_no()} pages")
    return output_path


if __name__ == "__main__":
    build_showcase_pdf()

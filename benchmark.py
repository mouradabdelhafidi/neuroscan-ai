"""Benchmark the current model against 160 labeled test images.

Computes: overall accuracy, per-class accuracy, confusion matrix,
and the 5 most confidently wrong predictions.
"""

import os
import torch
import torch.nn.functional as F
from transformers import AutoImageProcessor, SiglipForImageClassification
from PIL import Image
from collections import defaultdict

# ── CONFIG ───────────────────────────────────────────────────────────────────

MODEL_NAME = "prithivMLmods/BrainTumor-Classification-Mini"
BENCHMARK_DIR = "benchmark_images"

# The canonical class keys used in the benchmark dataset folders
GROUND_TRUTH_CLASSES = ["glioma", "meningioma", "notumor", "pituitary"]

# ── LOAD MODEL ───────────────────────────────────────────────────────────────

print(f"Loading model: {MODEL_NAME}")
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = SiglipForImageClassification.from_pretrained(MODEL_NAME)
model.eval()

# Show the model's label mapping
print(f"Model id2label: {model.config.id2label}")
print()

# ── NORMALIZE LABEL ──────────────────────────────────────────────────────────

def normalize_label(label_str):
    """Map a model output label or folder name to a canonical key."""
    s = label_str.lower().strip()
    if "glioma" in s:
        return "glioma"
    if "meningioma" in s:
        return "meningioma"
    if "pituitary" in s:
        return "pituitary"
    if "no" in s and "tumor" in s:
        return "notumor"
    return s

# ── RUN PREDICTIONS ──────────────────────────────────────────────────────────

results = []  # list of (true_label, pred_label, confidence, filepath)

for class_folder in sorted(os.listdir(BENCHMARK_DIR)):
    class_path = os.path.join(BENCHMARK_DIR, class_folder)
    if not os.path.isdir(class_path):
        continue

    true_label = normalize_label(class_folder)
    image_files = sorted([f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

    for img_file in image_files:
        img_path = os.path.join(class_path, img_file)
        image = Image.open(img_path).convert("RGB")

        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)

        logits = outputs.logits
        probs = F.softmax(logits, dim=-1).squeeze().tolist()
        class_names = [model.config.id2label[i] for i in range(len(model.config.id2label))]

        pred_idx = probs.index(max(probs))
        pred_label = normalize_label(class_names[pred_idx])
        confidence = probs[pred_idx]

        results.append((true_label, pred_label, confidence, img_path))

print(f"Total images evaluated: {len(results)}")
print()

# ── OVERALL ACCURACY ─────────────────────────────────────────────────────────

correct = sum(1 for t, p, _, _ in results if t == p)
total = len(results)
if total == 0:
    print("No benchmark images found. Run download_benchmark.py first.")
    exit(0)
print(f"Overall Accuracy: {correct}/{total} = {correct/total*100:.1f}%")
print()

# ── PER-CLASS ACCURACY ───────────────────────────────────────────────────────

print("Per-Class Accuracy:")
print(f"  {'Class':<15} {'Correct':>8} {'Total':>8} {'Accuracy':>10}")
print(f"  {'-'*43}")

class_correct = defaultdict(int)
class_total = defaultdict(int)

for true, pred, _, _ in results:
    class_total[true] += 1
    if true == pred:
        class_correct[true] += 1

for cls in GROUND_TRUTH_CLASSES:
    c = class_correct[cls]
    t = class_total[cls]
    acc = c / t * 100 if t > 0 else 0
    print(f"  {cls:<15} {c:>8} {t:>8} {acc:>9.1f}%")

print()

# ── CONFUSION MATRIX ─────────────────────────────────────────────────────────

print("Confusion Matrix (rows = true, columns = predicted):")
print()

# Build matrix
matrix = defaultdict(lambda: defaultdict(int))
for true, pred, _, _ in results:
    matrix[true][pred] += 1

# Header
row_label = "True \\ Pred"
header = f"  {row_label:<15}" + "".join(f"{cls:>12}" for cls in GROUND_TRUTH_CLASSES)
print(header)
print(f"  {'-' * (15 + 12 * len(GROUND_TRUTH_CLASSES))}")

for true_cls in GROUND_TRUTH_CLASSES:
    row = f"  {true_cls:<15}"
    for pred_cls in GROUND_TRUTH_CLASSES:
        count = matrix[true_cls][pred_cls]
        row += f"{count:>12}"
    print(row)

print()

# ── TOP 5 MOST CONFIDENTLY WRONG ─────────────────────────────────────────────

wrong = [(t, p, c, f) for t, p, c, f in results if t != p]
wrong.sort(key=lambda x: x[2], reverse=True)  # sort by confidence descending

print(f"Top 5 Most Confidently Wrong Predictions ({len(wrong)} total wrong):")
print(f"  {'Confidence':>11}  {'True':<15} {'Predicted':<15} {'File'}")
print(f"  {'-' * 70}")

for true, pred, conf, filepath in wrong[:5]:
    print(f"  {conf*100:>10.1f}%  {true:<15} {pred:<15} {os.path.basename(filepath)}")

print()
print("=== BENCHMARK COMPLETE ===")

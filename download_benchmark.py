"""Download 40 images per class for benchmarking.

Uses the HuggingFace Datasets Server parquet API to fetch pre-converted parquet
files directly, bypassing per-image HTTP requests and broken folder builders.
"""

import os
import random
import requests
import io
from collections import defaultdict
from PIL import Image
import pyarrow.parquet as pq

DEST_DIR = "benchmark_images"
SAMPLES_PER_CLASS = 40
SEED = 42
DATASET = "sartajbhuvaji/Brain-Tumor-Classification"

random.seed(SEED)

# Step 1: Get parquet file URLs from the HF Datasets Server API
print(f"Fetching parquet URLs for {DATASET}...")
api_url = f"https://datasets-server.huggingface.co/parquet?dataset={DATASET}"
resp = requests.get(api_url)
resp.raise_for_status()
info = resp.json()

print(f"Available splits/configs:")
for entry in info.get("parquet_files", []):
    print(f"  config={entry.get('config')}, split={entry.get('split')}, file={entry.get('filename')}, size={entry.get('size', 'N/A')}")

# Find the Testing split parquet files
test_files = [f for f in info["parquet_files"] if f["split"] == "Testing"]
if not test_files:
    # Fall back — list all splits and use whatever test split exists
    all_splits = set(f["split"] for f in info["parquet_files"])
    print(f"No 'Testing' split found. Available splits: {all_splits}")
    # Try common names
    for name in ["test", "Testing", "validation"]:
        test_files = [f for f in info["parquet_files"] if f["split"] == name]
        if test_files:
            break
    if not test_files:
        print("ERROR: No test split found. Using 'train' split instead.")
        test_files = [f for f in info["parquet_files"] if f["split"] == "Training"]

print(f"\nDownloading {len(test_files)} parquet file(s) for testing split...")

# Step 2: Download and read parquet files
all_images = []
all_labels = []

for pf in test_files:
    url = pf["url"]
    print(f"  Downloading {pf['filename']} ({pf.get('size', '?')} bytes)...")
    r = requests.get(url)
    r.raise_for_status()
    
    table = pq.read_table(io.BytesIO(r.content))
    df = table.to_pandas()
    print(f"    Columns: {list(df.columns)}, rows: {len(df)}")
    
    # The image column contains dicts with 'bytes' and 'path'
    for _, row in df.iterrows():
        img_data = row["image"]
        label = row["label"]
        
        # img_data is a dict with 'bytes' key containing the raw image bytes
        if isinstance(img_data, dict):
            img_bytes = img_data.get("bytes")
        else:
            img_bytes = img_data
        
        all_images.append(img_bytes)
        all_labels.append(label)

print(f"\nTotal images loaded: {len(all_images)}")

# Step 3: Figure out label names
unique_labels = sorted(set(all_labels))
print(f"Unique labels: {unique_labels}")

# Build label name mapping — labels might be ints or strings
# Common mapping for this dataset:
LABEL_MAP = {0: "glioma", 1: "meningioma", 2: "notumor", 3: "pituitary"}

# If labels are already strings, use them directly
if isinstance(unique_labels[0], str):
    label_to_name = {l: l.lower().replace(" ", "").replace("_", "") for l in unique_labels}
else:
    label_to_name = LABEL_MAP

print(f"Label mapping: {label_to_name}")

# Group by class
class_indices = defaultdict(list)
for i, label in enumerate(all_labels):
    class_indices[label].append(i)

print("\nClass distribution:")
for label in sorted(class_indices.keys()):
    name = label_to_name.get(label, str(label))
    print(f"  {name} (label={label}): {len(class_indices[label])} images")

# Step 4: Sample and save
saved_count = 0
for label, indices in sorted(class_indices.items()):
    class_name = label_to_name.get(label, str(label))
    class_dir = os.path.join(DEST_DIR, class_name)
    os.makedirs(class_dir, exist_ok=True)

    sampled = random.sample(indices, min(SAMPLES_PER_CLASS, len(indices)))
    for idx in sampled:
        img_bytes = all_images[idx]
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_path = os.path.join(class_dir, f"{class_name}_{idx:05d}.jpg")
        img.save(img_path, "JPEG")
        saved_count += 1

    print(f"  Saved {len(sampled)} images to {class_dir}/")

print(f"\nDone. {saved_count} total images saved to {DEST_DIR}/")

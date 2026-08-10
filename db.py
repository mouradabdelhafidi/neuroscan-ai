"""Database layer for persisting scan history using SQLite."""

import sqlite3
import os
import uuid
import json
from datetime import datetime
from PIL import Image

# ── CONFIGURATION ────────────────────────────────────────────────────────────

DB_PATH = "data/scans.db"
IMAGES_DIR = "data/images/"

# ── SCHEMA ───────────────────────────────────────────────────────────────────

def init_db():
    """Create the data directory and scans table if they don't already exist."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            name TEXT,
            image_path TEXT,
            prediction TEXT,
            confidence REAL,
            all_probabilities TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# ── CRUD OPERATIONS ──────────────────────────────────────────────────────────

def save_scan(name, image, predicted_class, confidence, all_probabilities):
    """Save a scan record (image file + DB row) and return its unique ID."""
    scan_id = str(uuid.uuid4())
    image_filename = f"{scan_id}.jpg"
    image_path = os.path.join(IMAGES_DIR, image_filename)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(image_path, "JPEG")
    
    timestamp = datetime.now().isoformat()
    probs_json = json.dumps(all_probabilities)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO scans (id, name, image_path, prediction, confidence, all_probabilities, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (scan_id, name, image_path, predicted_class, confidence, probs_json, timestamp))
    conn.commit()
    conn.close()
    return scan_id

def get_all_scans():
    """Return every saved scan as a list of dicts, newest first."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scans ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def search_scans_by_name(query):
    """Return scans whose name contains the query string (case-insensitive)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scans WHERE name LIKE ? ORDER BY created_at DESC', (f'%{query}%',))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_scan_by_id(scan_id):
    """Return a single scan dict by its UUID, or None if not found."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scans WHERE id = ?', (scan_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_scan(scan_id):
    """Delete a scan's DB record and its associated image file. Returns True on success."""
    scan = get_scan_by_id(scan_id)
    if scan:
        try:
            if os.path.exists(scan['image_path']):
                os.remove(scan['image_path'])
        except OSError:
            pass
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM scans WHERE id = ?', (scan_id,))
        conn.commit()
        conn.close()
        return True
    return False

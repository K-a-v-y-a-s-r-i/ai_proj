from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import json
from pathlib import Path
import numpy as np

# -----------------------------
# Configuration
# -----------------------------
# Use a valid biomedical NER model
MODEL = "d4data/biomedical-ner-all"

IN_FILE = Path("data/processed/passages.jsonl")
OUT_FILE = Path("data/processed/ner_predictions.jsonl")

if not IN_FILE.exists():
    raise SystemExit("Run preprocessing (passageize.py) first.")

# -----------------------------
# Load tokenizer and model
# -----------------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForTokenClassification.from_pretrained(MODEL)
nlp = pipeline(
    "ner",
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="simple"  # merge subword tokens
)

# -----------------------------
# Helper to convert NumPy types to native Python types
# -----------------------------
def convert_numpy(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    else:
        return obj

# -----------------------------
# Run NER inference
# -----------------------------
with open(IN_FILE, "r", encoding="utf-8") as fin, open(OUT_FILE, "w", encoding="utf-8") as fout:
    for line in fin:
        doc = json.loads(line)
        text = doc.get("text", "")
        try:
            ents = nlp(text)
            ents = convert_numpy(ents)
        except Exception as e:
            print("NER inference error:", e)
            ents = []
        doc["entities"] = ents
        fout.write(json.dumps(doc, ensure_ascii=False) + "\n")

print("Saved NER predictions:", OUT_FILE)

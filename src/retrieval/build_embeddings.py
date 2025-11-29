from sentence_transformers import SentenceTransformer
import numpy as np, json
from pathlib import Path

PASS_FILE = Path("data/processed/passages.jsonl")
OUT_EMB = Path("data/processed/embeddings.npy")
OUT_PASS = Path("data/processed/passages_list.json")

model_name = "sentence-transformers/all-mpnet-base-v2"  # change to biomedical SBERT if desired
model = SentenceTransformer(model_name)

passages = []
with open(PASS_FILE, "r", encoding="utf-8") as fin:
    for line in fin:
        rec = json.loads(line)
        passages.append(rec["text"])

print(f"Encoding {len(passages)} passages with {model_name} ...")
emb = model.encode(passages, show_progress_bar=True, convert_to_numpy=True)
np.save(OUT_EMB, emb)
with open(OUT_PASS, "w", encoding="utf-8") as f:
    json.dump(passages, f, ensure_ascii=False)
print("Saved embeddings:", OUT_EMB, "and passages:", OUT_PASS)

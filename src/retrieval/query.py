import faiss, json
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

INDEX = Path("models/faiss.index")
PASS = Path("data/processed/passages_list.json")

# Load sentence embedding model
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Load FAISS index
index = faiss.read_index(str(INDEX))

# Load passages
with open(PASS, "r", encoding="utf-8") as f:
    passages = json.load(f)

def retrieve(query: str, k: int = 5):
    """
    Retrieve top-k relevant passages for a query.
    """
    q_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, k)
    hits = []
    for i in range(len(I[0])):
        idx = int(I[0][i])
        hits.append({"score": float(D[0][i]), "idx": idx, "text": passages[idx]})
    return hits

if __name__ == "__main__":
    print("Test retrieve:", retrieve("BRCA1 breast cancer DNA repair", k=5))

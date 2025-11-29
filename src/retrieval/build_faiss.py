import faiss, numpy as np
from pathlib import Path

EMB = Path("data/processed/embeddings.npy")
IDX = Path("models/faiss.index")

emb = np.load(EMB)
# normalize for inner product search
faiss.normalize_L2(emb)
d = emb.shape[1]
index = faiss.IndexFlatIP(d)
index.add(emb)
faiss.write_index(index, str(IDX))
print("Saved FAISS index to", IDX)

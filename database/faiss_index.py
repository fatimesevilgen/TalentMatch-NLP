import faiss
import numpy as np
import os
import pickle

DIM = 384  # SBERT MiniLM output dimension
INDEX_PATH = "database/cv_faiss.index"
IDMAP_PATH = "database/cv_idmap.pkl"

# FAISS index
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
    with open(IDMAP_PATH, "rb") as f:
        id_map = pickle.load(f)
else:
    index = faiss.IndexFlatIP(DIM)
    id_map = []  # MongoDB _id listesi

def add_cv_embedding(embedding: np.ndarray, mongo_id: str):
    global index, id_map
    index.add(np.array([embedding]))
    id_map.append(mongo_id)
    faiss.write_index(index, INDEX_PATH)
    with open(IDMAP_PATH, "wb") as f:
        pickle.dump(id_map, f)

def search_similar(embedding: np.ndarray, top_k: int = 5):
    if index.ntotal == 0:
        return []
    D, I = index.search(np.array([embedding]), top_k)
    results = []
    for i, score in zip(I[0], D[0]):
        if i < len(id_map):
            results.append({"id": id_map[i], "score": float(score)})
    return results


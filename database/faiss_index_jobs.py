import faiss
import numpy as np
import os
import pickle

DIM = 384
INDEX_PATH = "database/job_faiss.index"
IDMAP_PATH = "database/job_idmap.pkl"

if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
    with open(IDMAP_PATH, "rb") as f:
        id_map = pickle.load(f)
else:
    index = faiss.IndexFlatIP(DIM)
    id_map = []

def add_job_embedding(embedding: np.ndarray, mongo_id: str):
    index.add(np.array([embedding]))
    id_map.append(mongo_id)
    faiss.write_index(index, INDEX_PATH)
    with open(IDMAP_PATH, "wb") as f:
        pickle.dump(id_map, f)

def get_all_job_embeddings():
    return index, id_map

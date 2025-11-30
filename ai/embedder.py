from sentence_transformers import SentenceTransformer
import numpy as np

# SBERT modeli (isteğe bağlı değiştirilebilir)
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def embed_text(text: str) -> np.ndarray:
    return model.encode(text, convert_to_numpy=True, normalize_embeddings=True)

import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from ai.parser import parse_cv
from ai.embedder import embed_text
from database.mongo_utils import save_cv_data
from database.faiss_index import add_cv_embedding
from database.faiss_index import search_similar
from database.mongo_utils import get_cv_by_id
from database.faiss_index import search_similar
from database.mongo_utils import get_cv_by_id
from database.faiss_index_jobs import add_job_embedding, get_all_job_embeddings
from database.mongo_utils import save_job_data, get_job_by_id
from score_utils import normalize_score
from bson import ObjectId
from database.mongo_utils import db  # Make sure db is imported from your mongo_utils or wherever it's defined


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # uploads klasörünü garantiye al

router = APIRouter()

# 1. Dosya yükleme
@router.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Sadece PDF veya DOCX dosyaları kabul edilir.")

    file_location = os.path.join(UPLOAD_DIR, filename)

    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    return JSONResponse(content={"message": "Dosya başarıyla yüklendi.", "filename": filename})


# 2. Parse işlemi
@router.post("/parse-cv")
async def parse_uploaded_cv(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dosya bulunamadı.")

    parsed_data = parse_cv(file_path)
    return parsed_data


# 3. MongoDB'ye kaydetme
@router.post("/store-cv")
async def store_parsed_cv(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dosya bulunamadı.")

    parsed_data = parse_cv(file_path)
    inserted_id = save_cv_data(filename, parsed_data)

    return {"message": "CV başarıyla kaydedildi", "cv_id": str(inserted_id)}


# 4. Vektörleme + Mongo + FAISS
@router.post("/index-cv")
async def index_cv(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dosya bulunamadı.")

    parsed_data = parse_cv(file_path)
    text_to_embed = parsed_data.get("summary") or parsed_data.get("raw_text")
    if not text_to_embed:
        raise HTTPException(status_code=422, detail="Embedlenecek metin bulunamadı.")

    embedding = embed_text(text_to_embed)
    mongo_id = save_cv_data(filename, parsed_data)
    add_cv_embedding(embedding, str(mongo_id))

    return {
        "message": "CV başarıyla vektörlendi ve indexlendi",
        "cv_id": str(mongo_id)
    }


# 5. CV arama
@router.post("/search-cv")
async def search_similar_cvs(text: str = None, filename: str = None, top_k: int = 5):
    if filename:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Dosya bulunamadı.")

        parsed_data = parse_cv(file_path)
        text = parsed_data.get("summary") or parsed_data.get("raw_text")

    if not text:
        raise HTTPException(status_code=400, detail="Arama için metin veya dosya adı gereklidir.")

    embedding = embed_text(text)
    similar_items = search_similar(embedding, top_k=top_k)

    matched_cvs = []
    for result in similar_items:  # ✅ DÜZELTİLDİ
        score = result["score"]
        percentage = normalize_score(score, method="l2")

        if percentage == 0.0:
            continue  # saçma skorlu sonuçları at

        cv = get_cv_by_id(result["id"])
        if cv:
            matched_cvs.append({
                "cv_id": result["id"],
                "match_percentage": percentage,
                "name": cv.get("name"),
                "email": cv.get("email"),
                "summary": cv.get("summary", "") or cv.get("raw_text", "")[:300]
            })

    return {"results": matched_cvs}



# İş ilanı yükleme ve indexleme
import numpy as np

@router.post("/upload-job")
async def upload_job(title: str, description: str):
    if not description:
        raise HTTPException(status_code=400, detail="İlan açıklaması boş olamaz.")

    embedding = embed_text(description)

    # ✅ float32 -> float
    embedding = [float(x) for x in embedding]

    job_id = save_job_data(title, description, embedding)
    add_job_embedding(embedding, job_id)

    return {"message": "İş ilanı kaydedildi ve indexlendi", "job_id": job_id}


# İş ilanı ile CV'leri eşleştirme
@router.post("/match-job-to-cvs")
async def match_job_to_candidates(job_id: str, top_k: int = 5):
    job = db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job ilanı bulunamadı.")

    embedding = job.get("embedding")
    if not embedding:
        raise HTTPException(status_code=400, detail="İlanın vektörü yok.")

    similar_items = search_similar(embedding, top_k=top_k)

    matched_cvs = []
    for item in similar_items:
        score = item["score"]
        percentage = normalize_score(score, method="cosine")  # skoru normalize et

        if percentage < 0.05:  # %5'ten düşük eşleşmeler filtrelensin (veya geçici olarak tamamen kaldır)
            continue

        cv = get_cv_by_id(item["id"])
        if cv:
            matched_cvs.append({
                "cv_id": str(item["id"]),
                "match_percentage": percentage,  # yüzdelik değer
                "name": cv.get("name"),
                "email": cv.get("email"),
                "summary": cv.get("summary", "") or cv.get("raw_text", "")[:300]
            })

    return {"results": matched_cvs}
from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId


# Bağlantı URI’si (default localhost)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI)
db = client["talentmatch"]
cv_collection = db["cvs"]

def save_cv_data(filename: str, parsed_data: dict):
    parsed_data["_filename"] = filename
    parsed_data["_createdAt"] = datetime.utcnow()
    result = cv_collection.insert_one(parsed_data)
    return str(result.inserted_id)


def get_cv_by_id(cv_id: str):
    return cv_collection.find_one({"_id": ObjectId(cv_id)})


job_collection = db["jobs"]


def get_job_by_id(job_id: str):
    return job_collection.find_one({"_id": ObjectId(job_id)})


def save_job_data(title, description, embedding=None):
    if embedding is None:
        print("UYARI: Embedding boş geliyor!")
    job_data = {
        "title": title,
        "description": description,
        "embedding": embedding
    }
    result = db.jobs.insert_one(job_data)
    return str(result.inserted_id)


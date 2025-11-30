# server/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes import upload  
from server.routes import upload  


app = FastAPI(title="TalentMatch NLP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)  # bu satırı ekle

@app.get("/")
def root():
    return {"message": "TalentMatch NLP API aktif!"}



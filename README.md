# 🧠 TalentMatch NLP  
### AI-Driven CV Analysis & Candidate Matching System

<div align="center">

🚀 **Python • spaCy • HuggingFace • FAISS • FastAPI • MongoDB • NLP**

</div>

---

## 📌 Proje Özeti

**TalentMatch NLP**, PDF/Docx formatındaki CV’leri otomatik analiz edip iş ilanlarıyla eşleştiren yapay zekâ destekli bir aday öneri sistemidir.  

Bu proje; doğal dil işleme, vektör arama ve modern web API teknolojilerini bir araya getirerek **otomatize işe alım süreçleri** için güçlü bir altyapı sunar.

---

## 🎯 Amaç

- Yüklenen CV’lerden eğitim, tecrübe ve beceri bilgilerini otomatik çıkarmak  
- CV ile iş ilanlarını NLP modelleri ile vektörleştirmek  
- FAISS kullanarak en uygun adayları hızlıca eşleştirmek  
- HR sistemlerinin API üzerinden otomatik aday sorgulaması yapabilmesini sağlamak  

---

## 🚀 Öne Çıkan Özellikler

### ✅ CV Yükleme (PDF / DOCX)
Kullanıcı PDF veya Docx CV dosyasını yükleyebilir.

### ✅ CV Bilgilerinin Otomatik Çıkarılması
spaCy + Regex + HF Token Classification ile bilgiler otomatik parse edilir:

- Ad Soyad  
- İletişim Bilgileri  
- Eğitim  
- Tecrübe  
- Beceriler  
- Özet Bölümü  

### ✅ İş İlanları Yönetimi  
Admin paneli üzerinden ilan oluşturma / düzenleme / silme desteklenir.

### ✅ SBERT + FAISS ile Vektörleştirme  
- CV → Embedding  
- İş İlanı → Embedding  

FAISS ile **milisaniyeler içinde benzerlik karşılaştırması** yapılır.

### ✅ Uygun Aday Skoru  
Her sonuç için:  
- ⭐ Uyum Oranı (%)  
- ❗ Eksik beceriler  
- 📌 Açıklama  

### ✅ Özet Rapor (Summarization)
HuggingFace extractive summarizer ile CV özeti üretilir.

### ✅ Bildirim Sistemi
E-mail veya SMS ile sonuç bildirimi yapılabilir.

### ✅ GDPR Uyumluluğu
- Veriler şifreli saklanır  
- Loglar kişisel veri içermez  
- Dökümanlar GridFS veya S3 üzerinde tutulur  

---

## 🛠️ Kullanılan Teknolojiler

| Alan | Teknoloji |
|------|-----------|
| Dil | Python 3.10+ |
| NLP | spaCy, HuggingFace Transformers, Sentence-BERT |
| Vektör Arama | FAISS |
| Backend | FastAPI |
| Database | MongoDB + GridFS |
| Depolama | GridFS veya Amazon S3 |
| PDF İşleme | pdfminer.six, PyMuPDF |
| Model Dağıtımı | Local HF Pipelines |

---

## 📦 Kurulum

### 1️⃣ Repo’yu Klonla
```bash
git clone https://github.com/<kullanıcı-adın>/talentmatch-nlp.git
cd talentmatch-nlp

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

MONGO_URI=mongodb://localhost:27017
DB_NAME=talentmatch
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

uvicorn server.main:app --reload

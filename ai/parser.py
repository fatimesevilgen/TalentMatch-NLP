import re
import pdfplumber
import docx
from langdetect import detect
import spacy

# SpaCy modelleri
spacy_models = {
    "en": spacy.load("en_core_web_sm"),
    "tr": spacy.load("tr_core_news_trf")  # önce başarıyla kurulduğunu kontrol et
}

# ----------------------- Dosya Okuyucular -----------------------

def read_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

def read_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# ----------------------- Dil Tespiti -----------------------

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except:
        return "en"

# ----------------------- Temel Bilgi Ayıklama -----------------------

def extract_email(text: str) -> str:
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else ""

def extract_phone(text: str) -> str:
    match = re.search(r"\b\d{10,11}\b", text.replace(" ", ""))
    return match.group() if match else ""

def extract_name(text: str, lang: str) -> str:
    doc = spacy_models[lang](text.strip().split("\n")[0])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return ""

# ----------------------- İngilizce CV İçin Bölüm Ayırıcı -----------------------

def extract_sections(text: str) -> dict:
    section_titles = [
        "SUMMARY", "SKILLS", "EDUCATION", "WORK EXPERIENCE", "PROJECT",
        "CERTIFICATES", "VOLUNTEER WORK", "CONTACT", "REFERENCES"
    ]

    pattern = r"(?i)^(" + "|".join(re.escape(t) for t in section_titles) + r")\s*$"
    lines = text.split("\n")

    sections = {}
    current_section = None
    buffer = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(pattern, line, re.IGNORECASE):
            if current_section and buffer:
                sections[current_section] = "\n".join(buffer).strip()
            current_section = line.upper()
            buffer = []
        elif current_section:
            buffer.append(line)

    if current_section and buffer:
        sections[current_section] = "\n".join(buffer).strip()

    return sections

# ----------------------- Türkçe CV İçin Keyword Ayıklayıcılar -----------------------

def extract_education(text: str, lang: str) -> list:
    lines = text.split("\n")
    keywords = ["üniversite", "bölüm", "öğrenim", "lisans", "yüksek lisans"]
    return [line.strip() for line in lines if any(k in line.lower() for k in keywords)]

def extract_experience(text: str, lang: str) -> list:
    lines = text.split("\n")
    keywords = ["staj", "çalıştı", "firma", "kurum", "mühendis", "görev", "pozisyon"]
    return [line.strip() for line in lines if any(k in line.lower() for k in keywords)]

def extract_skills(text: str) -> list:
    skill_list = ["python", "java", "c#", "sql", "git", "docker", "matplotlib", "numpy", "pandas", ".net", "spring"]
    return [skill for skill in skill_list if skill.lower() in text.lower()]

def extract_certificates(text: str) -> list:
    lines = text.split("\n")
    keywords = ["sertifika", "kurs", "akademi", "eğitim", "bootcamp", "udemy", "btk"]
    return [line.strip() for line in lines if any(k in line.lower() for k in keywords)]

def extract_references(text: str) -> list:
    lines = text.split("\n")
    keywords = ["referans", "gsm", "e-posta", "unvan", "firma"]
    return [line.strip() for line in lines if any(k in line.lower() for k in keywords)]

# ----------------------- Ana Parser Fonksiyonu -----------------------

def parse_cv(file_path: str) -> dict:
    if file_path.endswith(".pdf"):
        text = read_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = read_docx(file_path)
    else:
        return {}

    lang = detect_language(text)
    if lang not in spacy_models:
        lang = "en"

    name = extract_name(text, lang)
    email = extract_email(text)
    phone = extract_phone(text)

    if lang == "en":
        sections = extract_sections(text)
        parsed = {
            "lang": lang,
            "name": name,
            "email": email,
            "phone": phone,
            "summary": sections.get("SUMMARY", ""),
            "education": sections.get("EDUCATION", ""),
            "experience": sections.get("WORK EXPERIENCE", ""),
            "skills": sections.get("SKILLS", ""),
            "projects": sections.get("PROJECT", ""),
            "certificates": sections.get("CERTIFICATES", ""),
            "volunteer": sections.get("VOLUNTEER WORK", ""),
            "contact": sections.get("CONTACT", ""),
            "references": sections.get("REFERENCES", ""),
            "raw_text": text
        }
    else:
        parsed = {
            "lang": lang,
            "name": name,
            "email": email,
            "phone": phone,
            "education": extract_education(text, lang),
            "experience": extract_experience(text, lang),
            "skills": extract_skills(text),
            "certificates": extract_certificates(text),
            "references": extract_references(text),
            "raw_text": text
        }

    return parsed

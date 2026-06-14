from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import uuid
import datetime
import base64
import fitz  # PyMuPDF
import docx
import io

app = FastAPI()


class GeminiResult(BaseModel):
    classification: str
    sentiment: str
    confidence_score: float
    entities: dict


@app.get('/health')
def health_check():
    return {"status": "ok"}


@app.post('/enrich')
def enrich(data: GeminiResult):
    dept_map = {
        'quarterly_report': 'Management',
        'budget_update': 'BI & Analytics',
        'expense_claim': 'Finance'
    }

    return {
        'document_id': str(uuid.uuid4()),
        'department': dept_map.get(data.classification, 'General'),
        'sensitivity': 'high' if 'amounts' in str(data.entities).lower() else 'internal',
        'routing_tag': 'urgent-review' if data.confidence_score < 0.85 else 'auto-logged',
        'processed_at': datetime.datetime.utcnow().isoformat()
    }


@app.post('/extract_pdf')
async def extract_pdf(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        text = ""
        images = []

        for page in doc:
            text += page.get_text() + "\n"
            for img in page.get_images(full=True):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                images.append({
                    "mimeType": "image/" + base_image["ext"],
                    "data": base64_image
                })

        return {
            "extracted_text": text.strip(),
            "has_images": len(images) > 0,
            "vision_image": images[0] if len(images) > 0 else None
        }
    except Exception as e:
        return {"error": str(e)}


@app.post('/extract_docx')
async def extract_docx(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        doc = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

        return {
            "extracted_text": text.strip(),
            "has_images": False,
            "vision_image": None
        }
    except Exception as e:
        return {"error": str(e)}


@app.get('/categories')
def get_categories():
    return {
        "categories": [
            "invoice",
            "report",
            "contract",
            "ticket",
            "article",
            "other"
        ]
    }


class SensitivityRequest(BaseModel):
    document_text: str


@app.post('/sensitivity')
def classify_sensitivity(data: SensitivityRequest):
    text_lower = data.document_text.lower()

    if "confidential" in text_lower or "restricted" in text_lower:
        level = "confidential"
    elif "internal" in text_lower or "staff only" in text_lower:
        level = "internal"
    else:
        level = "public"

    return {"sensitivity_level": level}
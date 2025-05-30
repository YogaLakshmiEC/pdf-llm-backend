import os
import shutil
from datetime import datetime
from typing import List
from dotenv import load_dotenv
from bson.errors import InvalidId
from bson.objectid import ObjectId
from model import PdfUpload
import pdfplumber
from fastapi import FastAPI, UploadFile, File, HTTPException, Path
from database import collection
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY", "mock-key")
is_mock = api_key == "mock-key"

client = OpenAI(api_key=api_key) if not is_mock else None

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post('/upload', response_model=PdfUpload)
async def uploadPdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail='Only PDF files are allowed')


    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        full_text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                full_text += page.extract_text() or ""
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")

    pdf_record = {
        "pdf_name": file.filename,
        "upload_time": datetime.utcnow(),
        "text": full_text
    }
    result = collection.insert_one(pdf_record)
    return {
        "doc_id": str(result.inserted_id),
        "pdf_name": file.filename,
        "upload_time": pdf_record["upload_time"].isoformat(),
        "message": "PDF uploaded successfully."
    }

@app.get('/documents/{doc_id}', response_model=PdfUpload)
async def getPdfID(doc_id: str = Path(..., description="MongoDB document ID")):
    try:
        pdf = collection.find_one({'_id': ObjectId(doc_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    pdf["doc_id"] = str(pdf["_id"])
    return pdf


@app.post('/summarize/{doc_id}')
async def summaryPdf(doc_id: str):
    try:
        pdf = collection.find_one({'_id': ObjectId(doc_id)})
        if not pdf:
            raise HTTPException(status_code=404, detail="PDF not found")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")
    except Exception:
        raise HTTPException(status_code=500, detail="Error in retrieving PDF")
    text = pdf.get("text", "")
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text found to summarize")
    if is_mock:
        return {
            "doc_id": str(doc_id),
            "summary": "[MOCK] This is a summary for testing.",
            "warning": "Using mock response."
        }

    prompt = f"Summarize the following text in 2 sentences:\n\n{text[:50]}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=200
        )
        summary = response.choices[0].message.content.strip()
        return {"doc_id": str(doc_id), "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM summarization failed: {str(e)}")


@app.post("/Query/{doc_id}/{Question}")
async def pdfQuery(doc_id: str, Question: str):
    try:
        pdf = collection.find_one({"_id": ObjectId(doc_id)})
        if not pdf:
            raise HTTPException(status_code=404, detail="PDF not found")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    text = pdf.get("text", "")
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text found in the PDF")
    if is_mock:
        return {
            "doc_id": str(doc_id),
            "question": Question,
            "answer": "[MOCK] This is a answer to your question.",
            "warning": "Using mock response."
        }

    prompt = (
        f"Based on the following document content, answer the question accurately and concisely:\n\n"
        f"{text[:300]}\n\n"
        f"Question: {Question}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on a given document."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        answer = response.choices[0].message.content.strip()
        return {
            "doc_id": str(doc_id),
            "question": Question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/documents", response_model=List[PdfUpload])
async def get_documents(page: int = 1, limit: int = 10):
    try:
        skip = (page - 1) * limit
        cursor = collection.find().skip(skip).limit(limit)
        documents = []
        for doc in cursor:
            documents.append(PdfUpload(
                doc_id=str(doc["_id"]),
                pdf_name=doc.get("pdf_name", "unknown.pdf"),
                upload_time=doc.get("upload_time", datetime.utcnow())
            ))
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in retrieving PDFs: {str(e)}")
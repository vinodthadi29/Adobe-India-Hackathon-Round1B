from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import fitz  # PyMuPDF
import asyncio
import aiofiles
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import tempfile
import shutil

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize the embedding model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class DocumentSection(BaseModel):
    page: int
    rank: int
    score: float
    text: str
    summary: str

class DocumentAnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    persona: str
    job: str
    results: List[DocumentSection]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DocumentAnalysisRequest(BaseModel):
    persona: str
    job: str

# Helper functions
def clean_text(text: str) -> str:
    """Clean and normalize text"""
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with single newline
    text = text.strip()
    return text

def extract_text_from_pdf(pdf_path: str) -> List[dict]:
    """Extract text from PDF with page numbers"""
    doc = fitz.open(pdf_path)
    pages_text = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        if text.strip():  # Only add non-empty pages
            pages_text.append({
                "page": page_num + 1,
                "text": clean_text(text)
            })
    
    doc.close()
    return pages_text

def chunk_text(text: str, max_length: int = 500) -> List[str]:
    """Split text into chunks of reasonable size"""
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def generate_summary(text: str, max_length: int = 200) -> str:
    """Generate a simple extractive summary"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return text[:max_length]
    
    # Take first few sentences up to max_length
    summary = ""
    for sentence in sentences[:3]:  # Take first 3 sentences max
        if len(summary) + len(sentence) < max_length:
            summary += sentence + ". "
        else:
            break
    
    return summary.strip() if summary else text[:max_length]

async def process_documents(files: List[UploadFile], persona: str, job: str) -> DocumentAnalysisResult:
    """Process uploaded documents and return analysis results"""
    
    # Create query embedding
    query_text = f"Persona: {persona}. Job: {job}."
    query_embedding = model.encode([query_text])
    
    all_sections = []
    
    for file in files:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Extract text from PDF
            pages_text = extract_text_from_pdf(tmp_file_path)
            
            for page_data in pages_text:
                page_num = page_data["page"]
                text = page_data["text"]
                
                # Split text into chunks
                chunks = chunk_text(text)
                
                for chunk in chunks:
                    if len(chunk) < 50:  # Skip very short chunks
                        continue
                    
                    # Generate embedding for this chunk
                    chunk_embedding = model.encode([chunk])
                    
                    # Calculate similarity
                    similarity = cosine_similarity(query_embedding, chunk_embedding)[0][0]
                    
                    # Generate summary
                    summary = generate_summary(chunk)
                    
                    all_sections.append({
                        "page": page_num,
                        "text": chunk,
                        "score": float(similarity),
                        "summary": summary
                    })
        
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
    
    # Sort by score (descending) and take top 10
    all_sections.sort(key=lambda x: x["score"], reverse=True)
    top_sections = all_sections[:10]
    
    # Add rank
    for i, section in enumerate(top_sections):
        section["rank"] = i + 1
    
    # Create result
    result = DocumentAnalysisResult(
        persona=persona,
        job=job,
        results=[DocumentSection(**section) for section in top_sections]
    )
    
    # Save to database
    await db.document_analyses.insert_one(result.dict())
    
    return result

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Document Intelligence API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/analyze", response_model=DocumentAnalysisResult)
async def analyze_documents(
    persona: str = Form(...),
    job: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """Analyze uploaded documents for persona and job relevance"""
    
    # Validate inputs
    if not persona.strip() or not job.strip():
        raise HTTPException(status_code=400, detail="Persona and job are required")
    
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="At least one PDF file is required")
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
    
    # Validate file types
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
    
    try:
        result = await process_documents(files, persona, job)
        return result
    except Exception as e:
        logging.error(f"Error processing documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing documents")

@api_router.get("/analyses", response_model=List[DocumentAnalysisResult])
async def get_analyses():
    """Get all document analyses"""
    analyses = await db.document_analyses.find().sort("timestamp", -1).to_list(100)
    return [DocumentAnalysisResult(**analysis) for analysis in analyses]

@api_router.get("/analyses/{analysis_id}", response_model=DocumentAnalysisResult)
async def get_analysis(analysis_id: str):
    """Get specific document analysis"""
    analysis = await db.document_analyses.find_one({"id": analysis_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return DocumentAnalysisResult(**analysis)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
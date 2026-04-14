from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import shutil
from pathlib import Path
from .auth import authenticate_user, create_access_token, get_current_user
from .models import RunRequest, LoginRequest
from .pdf_parser import extract_text_from_pdf
from .analyzer import analyze_controls
from .database import save_findings, get_all_findings, get_findings_by_trace

app = FastAPI(title="SOC2 Audit Agent", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/api/token")
async def login(request: LoginRequest):
    if authenticate_user(request.username, request.password):
        token = create_access_token({"sub": request.username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...), user: str = Depends(get_current_user)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are allowed")
    
    # Save with unique name to avoid collisions
    safe_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(500, "Could not save file")
    
    return {"filename": safe_filename, "original_name": file.filename}

@app.post("/api/run")
async def run_audit(req: RunRequest, user: str = Depends(get_current_user)):
    # Find the most recently uploaded PDF
    pdf_files = sorted(UPLOAD_DIR.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not pdf_files:
        raise HTTPException(400, "No PDF uploaded yet. Please upload a document first.")
    
    latest_pdf = pdf_files[0]
    try:
        text = extract_text_from_pdf(str(latest_pdf))
    except Exception as e:
        raise HTTPException(500, f"Failed to extract text from PDF: {str(e)}")
    
    if len(text.strip()) < 100:
        raise HTTPException(400, "The PDF appears to contain no extractable text. It may be scanned/image-based.")
    
    findings = analyze_controls(req.control_ids, text)
    trace_id = str(uuid.uuid4())
    save_findings(trace_id, findings)
    
    return {"trace_id": trace_id, "findings": findings}

@app.get("/api/findings")
async def list_findings(user: str = Depends(get_current_user)):
    return get_all_findings()

@app.get("/api/findings/{trace_id}")
async def get_trace_findings(trace_id: str, user: str = Depends(get_current_user)):
    findings = get_findings_by_trace(trace_id)
    if not findings:
        raise HTTPException(404, "Trace not found")
    return {"trace_id": trace_id, "findings": findings}

@app.get("/api/health")
async def health():
    return {"status": "ok"}
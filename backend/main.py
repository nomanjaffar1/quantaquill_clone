from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pipeline import run_pipeline
import os

app = FastAPI(title="QuantaQuill API")

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    topic: str
    methodology: str = None
    experiments: str = None

@app.post("/generate")
def generate_paper(request: GenerateRequest):
    """
    Run the pipeline for the given topic and optional user inputs.
    """
    output_file = run_pipeline(request.topic, request.methodology, request.experiments)
    return {"message": "Paper generated successfully", "file_path": output_file}

@app.get("/download")
def download_pdf():
    pdf_path = "output/full_paper.pdf"
    if os.path.exists(pdf_path):
        return {"url": pdf_path}
    return {"error": "PDF not found"}

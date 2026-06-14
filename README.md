# Intelligent Cloud Document Analyst 🧠📄

A production-grade, multi-modal automated document processing pipeline. This project orchestrates document ingestion, AI-based extraction (via Google Gemini 3 Flash), and business logic enrichment to automate data entry into cloud databases.

## 🏗️ Architecture Overview
The system listens to a local directory for incoming files (`TXT`, `PDF`, `DOCX`). It extracts the text (and images for PDFs), sends the payload to Gemini for structured JSON classification, enriches the data via a local Python API, and finally dumps the output to Google Sheets, sends a Gmail alert, and saves a local Markdown summary.

## ⚙️ Prerequisites
* **n8n**: Running via Docker (access to local volumes required).
* **Python 3.10+**: For the FastAPI enrichment & extraction microservice.
* **Google Cloud**: Valid OAuth credentials for Sheets and Gmail nodes.
* **Gemini API Key**: From Google AI Studio.

## 🚀 Setup Instructions

### 1. The Python Microservice (Metadata & Parsing API)
This service handles DOCX/PDF parsing and adds business logic (department routing, sensitivity scoring).
1. Navigate to the project directory and install dependencies:
   `pip install fastapi uvicorn pydantic PyMuPDF python-docx python-multipart`
2. Start the server (listening on all interfaces so Docker can reach it):
   `uvicorn main:app --host 0.0.0.0 --port 5001 --reload`
3. Verify it's running by checking: `http://localhost:5001/health`

### 2. The n8n Workflow
1. Open your n8n instance (`http://localhost:5678`).
2. Go to **Workflows** -> **Import from File** and upload the provided `Financial_AI_Pipeline.json`.
3. **Credentials Setup**:
   * Open the Gemini node (`HTTPS Request: Gemini AI Analysis`) and set your `x-goog-api-key` in the Header Auth credential.
   * Authenticate the Google Sheets and Gmail nodes using OAuth2.
4. Update the Local File Trigger node to point to your specific `incoming_docs` directory path.

### ⚠️ Important Notes
* **Rate Limiting**: The free tier of Gemini limits requests to 15 RPM. A 2-second `Wait` node is implemented right before the Gemini API call to prevent `503 Service Unavailable` errors.
* **Local Network**: The n8n HTTP Request nodes use `http://host.docker.internal:5001` to communicate with the FastAPI server running on the host machine.
# Financial AI Pipeline 🧠📄

A production-grade, multi-modal automated document processing pipeline designed for financial document analysis and intelligent automation.

## 🌟 Key Features
* **Multi-Format Ingestion**: Supports `TXT`, `PDF`, and `DOCX` files.
* **Multi-Modal AI Engine**: Processes files as **multi-modal inputs**; utilizes Gemini Flash Vision to extract text *and* interpret embedded images, charts, and graphs within PDFs.
* **Enrichment Engine**: Routes documents to a local FastAPI microservice for metadata enrichment, department routing, and sensitivity classification.
* **Dual Output**: 
    * ☁️ Cloud: Automatically logs structured data to Google Sheets and sends professional alerts via Gmail.
    * 💾 Local: Exports a formatted `summary_*.md` file with AI-generated insights and entity extraction.

## ⚙️ Prerequisites
* **n8n**: Running via Docker (with local volume mapping).
* **Python 3.10+**: For the FastAPI enrichment service.
* **Dependencies**: `fastapi`, `uvicorn`, `pydantic`, `PyMuPDF`, `python-docx`, `python-multipart`.

## 🚀 Setup Instructions

### 1. The Python Microservice
1. Navigate to the project directory and locate the `microservice/` folder.
2. Install dependencies: `pip install fastapi uvicorn pydantic PyMuPDF python-docx python-multipart`
3. Start the server: `uvicorn main:app --host 0.0.0.0 --port 5001 --reload`.

### 2. The n8n Workflow
1. Import `Financial_AI_Pipeline.json` into your n8n instance.
2. **CRITICAL**: Ensure a directory named `output_docs/` exists in your local folder mapped to n8n (typically `/home/node/.n8n-files/output_docs/`). The pipeline requires this directory to save the generated Markdown reports.
3. Configure your credentials for Gemini (via Header Auth), Google Sheets, and Gmail (via OAuth2).
4. Update the **Local File Trigger** node to point to your `incoming_docs/` directory path.

## 🧪 Testing the Pipeline
* **PDFs**: Drop a financial report (PDF with charts) into the `incoming_docs` folder. The system will trigger the Vision capability to analyze both text and visual data.
* **DOCX/TXT**: The parser will extract content and route it through the FastAPI logic to classify the document (e.g., `quarterly_report`, `budget_update`).
* **Results**: 
    * Check your Google Sheet for the new row entry.
    * Check the `output_docs/` folder for the newly generated `.md` file containing the AI summary.

## ⚠️ Troubleshooting
* **Rate Limiting**: The Gemini API has request limits. A 2-second `Wait` node is implemented in the n8n workflow to prevent `503 Service Unavailable` errors.
* **Connectivity**: The n8n HTTP Request nodes use `http://host.docker.internal:5001` to communicate with the FastAPI server running on your host machine.
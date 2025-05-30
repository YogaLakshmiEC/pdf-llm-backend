### PDF Summarizer & Q&A API

A FastAPI application to upload PDFs, extract text, summarize content using OpenAI (or mock), and support document-based Q&A.

## Setup Instructions

1. Clone the Repository

git clone [https://github.com/your-username/pdf-api.git](https://github.com/YogaLakshmiEC/pdf-llm-backend.git)
cd pdf-llm-backend


2. Create and Activate a Virtual Environment

python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

3. Install Dependencies

pip install -r requirements.txt

4. Environment Variables
Create a .env file in the root directory with the following content:

MONGO_URI=mongodb://localhost:27017
DB_NAME=mydb
OPENAI_API_KEY=your-openai-key-or-mock-key

Use "mock-key" for OPENAI_API_KEY to test without OpenAI API access.

## Run the Application

Start the FastAPI server locally

uvicorn main:app --reload

Then open the interactive API docs at:

http://127.0.0.1:8000/docs

## Demo Video

https://drive.google.com/drive/folders/1ZxEncMx_tC0RWnVgdiUk0p41I3Bn0Ux1

## API Overview

| Method | Endpoint                     | Description                            |
| ------ | ---------------------------- | -------------------------------------- |
| POST   | `/upload`                    | Upload a PDF and extract text          |
| GET    | `/documents`                 | List PDFs with pagination              |
| GET    | `/documents/{doc_id}`        | Retrieve PDF metadata by ID            |
| POST   | `/summarize/{doc_id}`        | Summarize extracted PDF content        |
| POST   | `/Query/{doc_id}/{Question}` | Ask a question based on a specific PDF |

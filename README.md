# LangChain YouTube

A web app that lets you load a YouTube video by URL, then ask questions about its content using RAG (Retrieval-Augmented Generation) powered by LangChain and OpenAI.

## How it works

1. Paste a YouTube video URL on the search page
2. The backend fetches the transcript, chunks it, embeds it, and stores it in a FAISS vector index
3. Ask questions in the chat — relevant transcript chunks are retrieved and passed to the LLM for answers

## Stack

- **Frontend**: Angular 21 (standalone components, signals)
- **Backend**: FastAPI + LangChain + OpenAI + FAISS

## Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
OPENAI_API_KEY=your_key_here
```

Start the server:

```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
ng serve
```

Open `http://localhost:4200`

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v01/rest/load/{video_id}` | Fetch and embed YouTube transcript |
| POST | `/v01/rest/query/{video_id}` | Ask a question about the video |

import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel):
    question: str

@app.get("/v01/rest/load/{video_id}")
def load_transcript(video_id: str):
    try:
        path = f"indexes/{video_id}"

        if not os.path.exists(path):
            transcript_list = YouTubeTranscriptApi().fetch(video_id=video_id, languages=['en'])
            snippets = transcript_list.snippets
            transcript = " ".join([s.text for s in snippets])
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.create_documents([transcript])
            embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
            store = FAISS.from_documents(documents=chunks, embedding=embeddings)
            store.save_local(path)
            with open(f"{path}/history.json", "w") as f:
                json.dump([], f)

        with open(f"{path}/history.json", "r") as f:
            history = json.load(f)

        return JSONResponse(status_code=200, content={"message": f"Transcript: {video_id} loaded successfully", "history": history})

    except NoTranscriptFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post('/v01/rest/query/{video_id}')
def query_transcript(video_id: str, body: Request):
    try:
        path = f"indexes/{video_id}"

        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail=f"Transcript: {video_id} not found")

        # Load history
        history_path = f"{path}/history.json"
        with open(history_path, "r") as f:
            raw_history = json.load(f)

        history = [
            HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
            for m in raw_history
        ]

        # Retrieve context
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        store = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        retriever = store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        docs = retriever.invoke(body.question)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Build prompt with history
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Answer ONLY from the provided context. If the context is insufficient, say you don't know.\n\nContext:\n{context}"),
            MessagesPlaceholder("history"),
            ("human", "{question}")
        ])

        model = ChatOpenAI()
        chain = prompt | model
        result = chain.invoke({"context": context, "history": history, "question": body.question})

        # Save updated history
        raw_history.append({"role": "user", "content": body.question})
        raw_history.append({"role": "assistant", "content": result.content})
        with open(history_path, "w") as f:
            json.dump(raw_history, f, indent=2)

        return JSONResponse(status_code=200, content={"message": result.content})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
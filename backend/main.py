import os
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.prompts import PromptTemplate
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
        
        return JSONResponse(status_code=201, content={"message": f"Transcript: {video_id} loaded successfully"})

    except NoTranscriptFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post('/v01/rest/query/{video_id}')
def query_transcript(video_id: str, body: Request):
    try:
        path = f"indexes/{video_id}"

        if not os.path.exists(path):
            return HTTPException(status_code=404, detail="Transcript: {video_id} not found")
        
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        store = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        retriever = store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        context = retriever.invoke(body.question)

        template = PromptTemplate(
            template="""
                You are a helpful assistant.
                Answer ONLY from provided context.
                If the context is insufficient, just say you don't know.
                {context}

                Question: {question}
            """,
            input_variables=['context', 'question']
        )
        prompt = template.invoke({ "context": context, "question": body.question })
        model = ChatOpenAI()
        result = model.invoke(prompt)
        return JSONResponse(status_code=200, content={"message": result.content})

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
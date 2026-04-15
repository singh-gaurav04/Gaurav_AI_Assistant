from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import get_response
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG API. Send a POST request to /chat with your query."}

@app.post("/chat")
def chat(request: QueryRequest):
    response = get_response(request.query)
    return {"response": response}   

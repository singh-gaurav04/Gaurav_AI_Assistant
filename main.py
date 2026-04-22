from fastapi import FastAPI,Request
from pydantic import BaseModel
from rag_pipeline import get_response
from fastapi.middleware.cors import CORSMiddleware
import requests
from slack import post_to_slack
from utils.location import get_location 



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


@app.post("/track-visit")
async def track_visit(request: Request):
    data = await request.json()

    # ✅ Get IP
    ip = request.headers.get("x-forwarded-for", request.client.host)

    # 🌍 Get location
    location = get_location(ip)

    page = data.get("page", "unknown")
    user_agent = data.get("userAgent", "unknown")
    Referrer = data.get("referrer", "direct")

    # 📩 Slack message
    message = f"""
🚀 New Visitor

🌐 Page: {page}
📍 Location: {location}
💻 Device: {user_agent}
👉 Reference :{Referrer}
🧠 IP: {ip}
"""

    post_to_slack(message)

    return {"status": "tracked"}

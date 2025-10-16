from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from llm_pipeline import generate_response_stream, initialize_vector_db

app = FastAPI(title="Japanese Knowledge Base Chatbot")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    stream: bool = True

@app.on_event("startup")
async def startup_event():
    """Initialize vector database on startup"""
    print("Initializing vector database...")
    await initialize_vector_db()
    print("Vector database initialized!")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Japanese Knowledge Base Chatbot API"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat requests with optional streaming"""
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    if request.stream:
        # Return streaming response
        async def event_generator():
            async for chunk in generate_response_stream(request.query):
                yield f"data: {json.dumps({'text': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    else:
        # Return complete response
        full_response = ""
        async for chunk in generate_response_stream(request.query):
            full_response += chunk
        return {"answer": full_response}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


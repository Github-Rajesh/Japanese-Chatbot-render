from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from llm_pipeline import generate_response_stream, initialize_vector_db
from config import KNOWLEDGE_BASE_PATH
from pathlib import Path

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
    session_id: str | None = None

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
            async for chunk in generate_response_stream(request.query, request.session_id):
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


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF, save into the knowledge base, and (re)build the vectorstore.

    Saves files to `KNOWLEDGE_BASE_PATH/uploads/<filename>` and then triggers
    the RAG system to recreate the vectorstore so the new PDF is indexed.
    """
    # Basic validation
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    uploads_dir = Path(KNOWLEDGE_BASE_PATH) / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    save_path = uploads_dir / file.filename

    try:
        content = await file.read()
        with open(save_path, 'wb') as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Trigger rebuilding the vectorstore. We import the pipeline-level rag instance
    # which is initialized at startup via initialize_vector_db()
    try:
        # Import the current pipeline rag instance and call its incremental indexer
        from llm_pipeline import rag as pipeline_rag
        if pipeline_rag is None:
            # Try initialize if not yet created
            await initialize_vector_db()
            from llm_pipeline import rag as pipeline_rag

        # Prefer incremental indexing for speed and to make the file searchable immediately
        try:
            success = await pipeline_rag.add_documents_from_file(save_path)
            if not success:
                # Fallback to full rebuild
                await pipeline_rag.create_vectorstore()
        except AttributeError:
            # If incremental method not available, fall back to full rebuild
            await pipeline_rag.create_vectorstore()
    except Exception as e:
        # If indexing fails, still return success for upload but report indexing error
        return {"status": "uploaded", "path": str(save_path), "indexing": False, "error": str(e)}

    return {"status": "ok", "path": str(save_path), "indexing": True}


@app.get('/vector_sources')
async def vector_sources():
    """Return the list of indexed source filenames for quick inspection."""
    manifest = Path(Path(KNOWLEDGE_BASE_PATH).parent / 'data' / 'vectorstore') / 'sources.json'
    # The above path matches VECTORSTORE_PATH from config (BASE_DIR/data/vectorstore)
    if not manifest.exists():
        # Try known alt path
        manifest = Path(KNOWLEDGE_BASE_PATH) / 'uploads' / '..' / 'data' / 'vectorstore' / 'sources.json'
    try:
        import json
        if manifest.exists():
            with open(manifest, 'r', encoding='utf-8') as mf:
                data = json.load(mf)
            return {"sources": data}
        else:
            return {"sources": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read manifest: {e}")


@app.get('/debug_search')
async def debug_search(q: str):
    """Run a similarity search against the current vectorstore and return matched metadata.

    Use this to verify whether uploaded content is indexed and retrievable.
    """
    try:
        from llm_pipeline import rag as pipeline_rag
        if pipeline_rag is None or pipeline_rag.vectorstore is None:
            raise HTTPException(status_code=500, detail="Vectorstore not initialized")

        docs = pipeline_rag.vectorstore.similarity_search(q, k=5)
        results = []
        for d in docs:
            results.append({
                'source': d.metadata.get('source', 'unknown'),
                'page': d.metadata.get('page'),
                'text_preview': (d.page_content[:1000] + '...') if len(d.page_content) > 1000 else d.page_content
            })

        return {'query': q, 'hits': results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug search failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


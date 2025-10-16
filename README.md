# Japanese Knowledge Base Chatbot

Production-ready Japanese chatbot using **GPT-4o-mini** for reasoning and **RakutenAI** for natural Japanese language output. Features streaming responses and RAG (Retrieval Augmented Generation) from PDF documents.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.ai) installed
- OpenAI API key

### Installation

1. **Install Ollama & RakutenAI Model**
   ```bash
   # Download from https://ollama.ai
   ollama pull yuiseki/rakutenai-2.0-mini:1.5b-instruct
   ```

2. **Run Setup**
   ```bash
   setup.bat
   ```

3. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to `.env`

4. **Start Application**
   ```bash
   # Terminal 1 - Backend
   start_backend.bat
   
   # Terminal 2 - Frontend
   start_frontend.bat
   ```

5. **Open Browser**
   ```
   http://localhost:3000
   ```

## 📁 Project Structure

```
Japanese-chatbot/
├── backend/              # FastAPI application
│   ├── main.py          # Server with streaming
│   ├── llm_pipeline.py  # AI orchestration
│   ├── rag_system.py    # RAG with ChromaDB
│   └── config.py        # Configuration
├── frontend/            # Web interface
│   ├── index.html       # Main UI
│   ├── styles.css       # Styling
│   └── app.js           # Chat logic
├── knowledge base main/ # Your PDF documents
├── setup.bat           # Setup script
├── start_backend.bat   # Start backend
└── start_frontend.bat  # Start frontend
```

## 🎯 Features

- ✅ **Streaming Responses** - Real-time text generation (3-5 seconds)
- ✅ **RAG System** - Semantic search over PDF knowledge base
- ✅ **Dual-Model** - GPT-4o-mini (reasoning) + RakutenAI (natural Japanese)
- ✅ **Claude-like UI** - Professional dark theme interface
- ✅ **Production Ready** - Error handling, CORS, async/await

## 🔧 Configuration

Edit `backend/config.py` to customize:
- Model selection
- RAG parameters (chunk size, retrieval count)
- Paths and directories

## 📝 Usage

1. Type your question in Japanese
2. Watch the response stream in real-time
3. First query takes 2-5 minutes (one-time PDF indexing)
4. Subsequent queries: 3-5 seconds

## 🛠️ Tech Stack

- **Backend**: FastAPI, OpenAI GPT-4o-mini, Ollama/RakutenAI
- **RAG**: LangChain, ChromaDB, Sentence Transformers
- **Frontend**: Vanilla JavaScript, CSS3
- **Documents**: PyPDF for PDF processing

## 📄 License

All rights reserved.

## 🙋 Support

For issues:
1. Ensure Ollama is running
2. Check `.env` file has valid API key
3. Verify Python 3.9+ is installed
4. Check ports 8000 and 3000 are available


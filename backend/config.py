import os
from pathlib import Path
from dotenv import load_dotenv

# Paths
BASE_DIR = Path(__file__).parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables from root directory
load_dotenv(dotenv_path=ENV_PATH)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Debug: Check if .env file exists and API key is loaded
if not ENV_PATH.exists():
    print(f"WARNING: .env file not found at {ENV_PATH}")
else:
    print(f"✓ .env file found at {ENV_PATH}")

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not loaded from .env file!")
    print(f"Please check {ENV_PATH} file")
else:
    print(f"✓ OPENAI_API_KEY loaded (length: {len(OPENAI_API_KEY)} chars)")

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Additional paths
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge base main"
VECTORSTORE_PATH = BASE_DIR / "data" / "vectorstore"

# Model Configuration
GPT_MODEL = "gpt-4o-mini"
RAKUTEN_MODEL = "yuiseki/rakutenai-2.0-mini:1.5b-instruct"

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RETRIEVAL_K = 4

# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"


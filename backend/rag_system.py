import os
from typing import List
from pathlib import Path
import asyncio
from config import KNOWLEDGE_BASE_PATH, VECTORSTORE_PATH, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, RETRIEVAL_K

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import PyPDFLoader, UnstructuredExcelLoader
    from langchain.schema import Document
except ImportError:
    print("Warning: langchain packages not installed. Install with: pip install langchain langchain-community")

class RAGSystem:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.knowledge_base_path = KNOWLEDGE_BASE_PATH
        self.persist_directory = VECTORSTORE_PATH
        
    async def initialize(self):
        """Initialize or load the vector database"""
        # Create embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        
        # Check if vectorstore exists
        if self.persist_directory.exists() and len(list(self.persist_directory.iterdir())) > 0:
            print("Loading existing vector database...")
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings
            )
        else:
            print("Creating new vector database...")
            await self.create_vectorstore()
    
    async def create_vectorstore(self):
        """Create vector database from knowledge base files"""
        documents = []
        
        # Load all PDF files
        pdf_files = list(self.knowledge_base_path.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in pdf_files:
            try:
                print(f"Loading: {pdf_file.name}")
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading {pdf_file.name}: {e}")
        
        # Load Excel files
        excel_files = list(self.knowledge_base_path.glob("*.xlsx"))
        print(f"Found {len(excel_files)} Excel files")
        
        for excel_file in excel_files:
            try:
                print(f"Loading: {excel_file.name}")
                loader = UnstructuredExcelLoader(str(excel_file), mode="elements")
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading {excel_file.name}: {e}")
        
        if not documents:
            print("Warning: No documents loaded from knowledge base")
            # Create empty vectorstore
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings
            )
            return
        
        print(f"Total documents loaded: {len(documents)}")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks")
        
        # Create vectorstore
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=str(self.persist_directory)
        )
        print("Vector database created and persisted!")
    
    async def retrieve_context(self, query: str, k: int = RETRIEVAL_K) -> str:
        """Retrieve relevant context for a query"""
        if self.vectorstore is None:
            return ""
        
        try:
            # Perform similarity search
            docs = self.vectorstore.similarity_search(query, k=k)
            
            # Combine documents into context
            context_parts = []
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', 'N/A')
                context_parts.append(f"[出典 {i}: {Path(source).name} - ページ {page}]\n{doc.page_content}")
            
            return "\n\n".join(context_parts)
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return ""


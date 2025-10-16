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

# Import vertical Japanese PDF handler
try:
    from vertical_japanese import extract_text_from_pdf as extract_vertical_pdf
except ImportError:
    print("Warning: vertical_japanese module not found. Vertical Japanese PDFs may not be processed correctly.")
    extract_vertical_pdf = None

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
    
    def _load_vertical_pdf(self, pdf_path: Path) -> List[Document]:
        """Load PDF with vertical Japanese text using OCR"""
        if extract_vertical_pdf is None:
            print(f"Warning: Vertical Japanese handler not available. Falling back to standard loader.")
            loader = PyPDFLoader(str(pdf_path))
            return loader.load()
        
        try:
            print(f"Using vertical Japanese OCR for: {pdf_path.name}")
            result = extract_vertical_pdf(str(pdf_path), lang="jpn_vert", clean_text=True)
            
            if result['success']:
                # Create a Document for each page
                docs = []
                for page_num, page_text in enumerate(result['pages'], start=1):
                    if page_text.strip():  # Only add non-empty pages
                        doc = Document(
                            page_content=page_text,
                            metadata={
                                'source': str(pdf_path),
                                'page': page_num,
                                'type': 'vertical_japanese',
                                'total_pages': result['page_count']
                            }
                        )
                        docs.append(doc)
                return docs
            else:
                print(f"OCR failed for {pdf_path.name}: {result['error']}. Falling back to standard loader.")
                loader = PyPDFLoader(str(pdf_path))
                return loader.load()
        except Exception as e:
            print(f"Error in vertical PDF loading {pdf_path.name}: {e}. Falling back to standard loader.")
            loader = PyPDFLoader(str(pdf_path))
            return loader.load()
    
    async def create_vectorstore(self):
        """Create vector database from knowledge base files (including subdirectories)"""
        documents = []
        
        # Recursively find all PDF files in knowledge base and subdirectories
        pdf_files = list(self.knowledge_base_path.rglob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files (including subdirectories)")
        
        for pdf_file in pdf_files:
            try:
                # Get relative path from knowledge base
                rel_path = pdf_file.relative_to(self.knowledge_base_path)
                print(f"Loading: {rel_path}")
                
                # Check if PDF is in "Verticle writing" folder (note the typo in folder name)
                if "Verticle writing" in str(rel_path) or "Vertical writing" in str(rel_path):
                    # Use vertical Japanese handler
                    docs = self._load_vertical_pdf(pdf_file)
                    documents.extend(docs)
                else:
                    # Use standard PDF loader
                    loader = PyPDFLoader(str(pdf_file))
                    docs = loader.load()
                    documents.extend(docs)
                    
            except Exception as e:
                print(f"Error loading {pdf_file.name}: {e}")
        
        # Recursively find all Excel files
        excel_files = list(self.knowledge_base_path.rglob("*.xlsx"))
        print(f"Found {len(excel_files)} Excel files (including subdirectories)")
        
        for excel_file in excel_files:
            try:
                rel_path = excel_file.relative_to(self.knowledge_base_path)
                print(f"Loading: {rel_path}")
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


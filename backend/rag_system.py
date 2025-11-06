import os
from typing import List
from pathlib import Path
import asyncio
from config import KNOWLEDGE_BASE_PATH, VECTORSTORE_PATH, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, RETRIEVAL_K

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredExcelLoader
from langchain.schema import Document

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
        self.conversation_vectorstore = None
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

        # Initialize (or load) conversation vectorstore (separate namespace)
        try:
            conv_dir = Path(self.persist_directory) / 'conversations'
            if conv_dir.exists() and len(list(conv_dir.iterdir())) > 0:
                print("Loading existing conversation vectorstore...")
                self.conversation_vectorstore = Chroma(
                    persist_directory=str(conv_dir),
                    embedding_function=self.embeddings
                )
            else:
                print("Creating new conversation vectorstore (empty)...")
                conv_dir.mkdir(parents=True, exist_ok=True)
                # create an empty Chroma instance
                self.conversation_vectorstore = Chroma(
                    persist_directory=str(conv_dir),
                    embedding_function=self.embeddings
                )
        except Exception as e:
            print(f"Failed to initialize conversation vectorstore: {e}")
    
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
                # Fallback: try to read Excel with pandas and convert to simple text
                try:
                    import pandas as pd
                    sheets = pd.read_excel(str(excel_file), sheet_name=None)
                    for sheet_name, df in sheets.items():
                        text = df.fillna('').astype(str).to_csv(index=False)
                        doc = Document(
                            page_content=text,
                            metadata={'source': str(excel_file), 'sheet': sheet_name}
                        )
                        documents.append(doc)
                    print(f"Loaded {excel_file.name} via pandas fallback")
                except Exception as e2:
                    print(f"Pandas fallback failed for {excel_file.name}: {e2}")
        
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
        
        # Write a small manifest of sources for quick inspection
        try:
            sources = {Path(doc.metadata.get('source', '')).name for doc in documents if doc.metadata.get('source')}
            manifest_path = Path(self.persist_directory) / 'sources.json'
            import json
            with open(manifest_path, 'w', encoding='utf-8') as mf:
                json.dump(sorted(list(sources)), mf, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to write sources manifest: {e}")

    async def add_documents_from_file(self, file_path: Path):
        """Incrementally add documents from a single file to the existing vectorstore.

        This tries to load the file (respecting vertical PDFs), split into chunks,
        and add them to the current Chroma vectorstore. If the vectorstore doesn't
        exist yet, it will create it from the single file.
        """
        try:
            # Load file into Documents list
            if str(file_path).lower().endswith('.pdf'):
                # Use vertical loader if appropriate
                rel_path = file_path.relative_to(self.knowledge_base_path) if self.knowledge_base_path in file_path.parents else file_path
                if "Verticle writing" in str(rel_path) or "Vertical writing" in str(rel_path):
                    docs = self._load_vertical_pdf(file_path)
                else:
                    loader = PyPDFLoader(str(file_path))
                    docs = loader.load()
            elif str(file_path).lower().endswith('.xlsx') or str(file_path).lower().endswith('.xls'):
                try:
                    loader = UnstructuredExcelLoader(str(file_path), mode="elements")
                    docs = loader.load()
                except Exception:
                    # pandas fallback
                    import pandas as pd
                    sheets = pd.read_excel(str(file_path), sheet_name=None)
                    docs = []
                    for sheet_name, df in sheets.items():
                        text = df.fillna('').astype(str).to_csv(index=False)
                        doc = Document(
                            page_content=text,
                            metadata={'source': str(file_path), 'sheet': sheet_name}
                        )
                        docs.append(doc)
            else:
                # Unsupported type: return
                print(f"Unsupported file type for incremental indexing: {file_path}")
                return False

            if not docs:
                print(f"No documents extracted from {file_path}")
                return False

            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                length_function=len,
            )
            chunks = text_splitter.split_documents(docs)

            # If vectorstore doesn't exist, create it from these chunks
            if self.vectorstore is None:
                print("Vectorstore not present; creating new vectorstore from uploaded file...")
                self.persist_directory.mkdir(parents=True, exist_ok=True)
                self.vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=str(self.persist_directory)
                )
            else:
                print(f"Adding {len(chunks)} chunks to existing vectorstore...")
                try:
                    # LangChain vectorstore API: add_documents
                    self.vectorstore.add_documents(chunks)
                except Exception as e:
                    print(f"add_documents failed: {e} -- falling back to full rebuild")
                    # On failure, rebuild entire vectorstore to ensure consistency
                    await self.create_vectorstore()
                    return True

            # Update sources manifest
            try:
                # Try to update manifest by reading existing manifest and adding this source
                import json
                manifest_path = Path(self.persist_directory) / 'sources.json'
                existing = []
                if manifest_path.exists():
                    with open(manifest_path, 'r', encoding='utf-8') as mf:
                        existing = json.load(mf)
                src_name = Path(str(file_path)).name
                existing = list(sorted(set(existing + [src_name])))
                with open(manifest_path, 'w', encoding='utf-8') as mf:
                    json.dump(existing, mf, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Failed to update sources manifest: {e}")

            # Try to persist if supported
            try:
                persist_fn = getattr(self.vectorstore, 'persist', None)
                if callable(persist_fn):
                    persist_fn()
            except Exception:
                pass

            print(f"Incremental indexing complete for: {file_path.name}")
            return True
        except Exception as e:
            print(f"Error in incremental indexing {file_path.name}: {e}")
            return False

    async def add_conversation_turn(self, session_id: str, role: str, text: str):
        """Add a single conversation turn (user or assistant) to the conversation vectorstore.

        session_id is stored in metadata so we can filter or retrieve per session.
        """
        try:
            if not self.conversation_vectorstore:
                print("Conversation vectorstore not initialized; skipping add_conversation_turn")
                return False

            # Create a Document for the turn
            from datetime import datetime
            doc = Document(
                page_content=text,
                metadata={
                    'source': 'conversation',
                    'session': session_id,
                    'role': role,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )

            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                length_function=len,
            )
            chunks = text_splitter.split_documents([doc])

            # Add to conversation vectorstore
            try:
                self.conversation_vectorstore.add_documents(chunks)
            except Exception as e:
                print(f"conversation_vectorstore.add_documents failed: {e}")
                return False

            # Persist if available
            try:
                persist_fn = getattr(self.conversation_vectorstore, 'persist', None)
                if callable(persist_fn):
                    persist_fn()
            except Exception:
                pass

            return True
        except Exception as e:
            print(f"Error adding conversation turn: {e}")
            return False
    async def retrieve_context(self, query: str, k: int = RETRIEVAL_K) -> str:
        """Retrieve relevant context for a query"""
        if self.vectorstore is None:
            return ""
        
        try:
            # Perform similarity search
            docs = self.vectorstore.similarity_search(query, k=k)
            
            # Combine documents into context
            context_parts = []
            rag_sources = []
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', 'N/A')
                rag_sources.append({'source': str(source), 'page': page, 'preview': doc.page_content[:200]})
                context_parts.append(f"[出典 {i}: {Path(source).name} - ページ {page}]\n{doc.page_content}")

            # Also retrieve conversation-based context (semantic matches from recent conversations)
            convo_parts = []
            convo_sources = []
            try:
                if self.conversation_vectorstore is not None:
                    convo_docs = self.conversation_vectorstore.similarity_search(query, k=k)
                    for j, cdoc in enumerate(convo_docs, 1):
                        session = cdoc.metadata.get('session', 'unknown')
                        role = cdoc.metadata.get('role', 'unknown')
                        convo_sources.append({'session': session, 'role': role, 'preview': cdoc.page_content[:200]})
                        convo_parts.append(f"[会話 ({role}) セッション:{session}]\n{cdoc.page_content}")
            except Exception as e:
                print(f"Error retrieving conversation context: {e}")

            # Debug logging: print which sources were matched for this query
            try:
                print(f"retrieve_context: query=\"{query}\" -> {len(rag_sources)} RAG hits, {len(convo_sources)} convo hits")
                if rag_sources:
                    print("RAG hits (top):", rag_sources[:min(5, len(rag_sources))])
                if convo_sources:
                    print("Conversation hits (top):", convo_sources[:min(5, len(convo_sources))])
            except Exception:
                pass

            # Combine RAG docs first, then conversation snippets
            all_parts = context_parts + convo_parts
            return "\n\n".join(all_parts)
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return ""


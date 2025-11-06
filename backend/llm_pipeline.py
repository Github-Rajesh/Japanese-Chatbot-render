import os
import asyncio
import subprocess
from typing import AsyncGenerator
from openai import AsyncOpenAI
from rag_system import RAGSystem
from config import OPENAI_API_KEY, GPT_MODEL, RAKUTEN_MODEL, MAX_RESPONSE_TOKENS, RESPONSE_TEMPERATURE

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Initialize RAG system
rag = None

async def initialize_vector_db():
    """Initialize the RAG system"""
    global rag
    rag = RAGSystem()
    await rag.initialize()

async def query_gpt4o_mini_stream(user_query: str, context: str) -> AsyncGenerator[str, None]:
    """Query GPT-4o-mini with streaming support"""
    prompt = f"""あなたは日本の建築・法律に関する専門的な知識ベースアシスタントです。
提供されたコンテキストを使用して、質問に正確かつ詳細に答えてください。

コンテキスト:
{context}

質問:
{user_query}

回答は日本語で、事実に基づいて包括的に答えてください。必要に応じて、詳細な説明、具体例、関連する法令や規則の引用を含めてください。"""

    try:
        stream = await client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "あなたは論理的推論と知識検索を担当する専門アシスタントです。質問の内容に応じて、必要な詳細を全て含んだ包括的で正確な回答を提供してください。"},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            temperature=RESPONSE_TEMPERATURE,
            max_tokens=MAX_RESPONSE_TOKENS
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        print(f"Error in GPT-4o-mini: {e}")
        yield f"エラーが発生しました: {str(e)}"

def refine_with_rakutenai(text: str) -> str:
    """Refine text with RakutenAI for natural Japanese"""
    rakuten_prompt = f"""以下のテキストを自然な敬語のビジネス日本語に書き直してください。
不自然な直訳を避け、読みやすく、顧客向けのトーンに整えてください。
専門用語はそのまま保持してください。

原文:
{text}

改善された日本語:"""
    
    try:
        result = subprocess.run(
            ["ollama", "run", RAKUTEN_MODEL, "-p", rakuten_prompt],
            capture_output=True,
            text=True,
            timeout=10
        )
        refined = result.stdout.strip()
        return refined if refined else text
    except subprocess.TimeoutExpired:
        print("RakutenAI timeout - returning original text")
        return text
    except Exception as e:
        print(f"Error in RakutenAI: {e} - returning original text")
        return text

async def generate_response_stream(user_query: str, session_id: str | None = None) -> AsyncGenerator[str, None]:
    """Generate streaming response through the full pipeline.

    If session_id is provided, the user turn and assistant turn will be added
    to the conversation vectorstore so they become part of conversational memory.
    """

    # Ensure RAG system initialized
    if rag is None:
        await initialize_vector_db()

    # If session_id provided, log the user turn into conversation memory
    if session_id is not None and rag is not None:
        try:
            await rag.add_conversation_turn(session_id, 'user', user_query)
        except Exception as e:
            print(f"Warning: failed to add user conversation turn: {e}")

    # Step 1: Retrieve context from knowledge base + conversation memory
    context = await rag.retrieve_context(user_query) if rag is not None else ""

    # Step 2: Stream response from GPT-4o-mini
    draft_response = ""
    async for chunk in query_gpt4o_mini_stream(user_query, context):
        draft_response += chunk
        yield chunk
    
    # Note: For better UX with streaming, we skip RakutenAI refinement during streaming
    # RakutenAI can be used for non-streaming responses or as a separate refinement pass
    
    # Optional: Add a refinement pass (currently disabled for speed)
    # This can be enabled for non-streaming responses
    # refined = await asyncio.to_thread(refine_with_rakutenai, draft_response)

    # If session_id provided, add the assistant turn to conversation memory
    if session_id is not None and rag is not None:
        try:
            await rag.add_conversation_turn(session_id, 'assistant', draft_response)
        except Exception as e:
            print(f"Warning: failed to add assistant conversation turn: {e}")


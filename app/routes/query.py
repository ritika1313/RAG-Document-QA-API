from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI

# load .env from project root
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

gemini_client = ChatGoogleGenerativeAI(model="gemini-3.8-flash")
router = APIRouter(
    prefix="/query",
    tags=["query"],
)
embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    collection_name="sample_collection",
    url="http://localhost:6333"
)

@router.post("/")
async def query(question: str):
    search_results = vector_db.similarity_search(query=question)
    context = "\n\n".join(
        [
            f"[Page {result.metadata.get('page', 'unknown')}] {result.page_content}"
            for result in search_results
        ]
    )

    system_prompt = f"""
You are a helpful assistant that answers questions based on the provided context.
If the context does not contain the answer, respond with "I don't know."
Include the page number of the context in your answer when applicable.

Context:
{context}
"""
    response = gemini_client.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=question),
        ],
    )
    return {"question": question, "answer": response.content}

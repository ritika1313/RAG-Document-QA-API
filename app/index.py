from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

app = FastAPI()


pdf_path = Path(__file__).parent.parent / "data" / "sample.pdf"

# PDF Loading
loader = PyPDFLoader(str(pdf_path))
docs = loader.load()

# Split documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

chunks = text_splitter.split_documents(documents=docs)

# Gemini embeddings
embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

# Qdrant
vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    collection_name="sample_collection",
    url="http://localhost:6333"
)

print("Vector store created and documents embedded successfully")


@app.get("/")
def home():
    return {"message": "RAG API is running"}
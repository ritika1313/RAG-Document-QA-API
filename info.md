# 1. What is RAG?
- RAG stands for Retrieval-Augmented Generation.
- RAG is a technique used to make an LLM answer questions using
- information from an external knowledge source, such as: PDFs, Documents, Websites, Databases, Company data.
- Instead of asking the LLM to answer only from its existing knowledge, RAG first retrieves relevant information and then gives that information to the LLM as context.
* RAG = Retrieve relevant information + Give it to the LLM + Generate the answer

# 2. Why do we need RAG?
Suppose we have a private PDF containing project information.
A normal LLM does not automatically have access to that PDF.
RAG solves this problem by creating a searchable knowledge base from the PDF.

* Without RAG:                                         * With RAG 
User Question                                         User Question 
       |                                                   |
    LLM                                           Search relevent information
        |                                                   |
    Answer from its existing know                     Reterive relevant chunks
                                                           |
                                                    Give chunks + question to LLM
                                                           | 
                                                    Final Answer


# 3. RAG has Two Main Pipelines
## A. Indexing / Ingestion Pipeline
This prepares the documents so that they can be searched later.
    PDF
    ↓
   Load
    ↓
Split into chunks
     ↓
Create embeddings
     ↓
Store in vector database

## B. Query / Retrieval + Generation Pipeline
This handles the user's question.
User Question
    ↓
Similarity Search
     ↓
Retrieve relevant chunks
     ↓
Create context
     ↓
Send context + question to LLM
      ↓
Generate Answer

# 4. My RAG Pipeline
In my project, the main components are:
- Component                        Purpose
- PDF                              Source of knowledge
- PyPDFLoader                      Loads the PDF
- RecursiveCharacterTextSplitter   Splits the document into chunks
- GoogleGenerativeAIEmbeddings     Converts text into vectors
- Qdrant                           Stores and searches vectors
- Gemini Chat Model                Generates the final answer
- FastAPI                          Provides the API endpoint
The overall architecture is:
                    INDEXING PIPELINE

                   sample.pdf
                       ↓
                 PyPDFLoader
                       ↓
                   Documents
                       ↓
            RecursiveCharacterTextSplitter
                       ↓
                    Chunks
                       ↓
              Embedding Model
                       ↓
                  Embeddings
                       ↓
                    Qdrant
                       ↓
              sample_collection


                     QUERY PIPELINE

                  User Question
                       ↓
                FastAPI Endpoint
                       ↓
               Similarity Search
                       ↓
                     Qdrant
                       ↓
               Relevant Chunks
                       ↓
                    Context
                       ↓
              Gemini Chat Model
                       ↓
                 Final Answer

# Step1: Document Loading:
My code uses:
loader = PyPDFLoader(str(pdf_path))
docs = loader.load()
- PyPDFLoader reads the PDF and converts its content into document objects.

# Step2: Chunking
- A large document should not be treated as one huge piece of text.
- Therefore, we split the document into smaller pieces called chunks.
My code uses:
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,          # splitter tries to create chunks of roughly 1000 character
    chunk_overlap=200,        # neighbouring chunks share some content
)
 - Q1. Why use Overlap?
It helps us prevent context when an important piece of information is near the boundary between two chunks.

# Step3: Embeddings
My project uses:
embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)
- An embedding is a numerical vector representation of text that captures its semantic meaning.

# Step4: Vector Database
- My project uses Qdrant as the vector database.
- The embeddings generated from the document chunks are stored in Qdrant.
- Qdrant allows us to search for vectors that are similar to the vector representation of a user's question.

# Step5: Storing the Documents
The indexing code uses:
vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    collection_name="sample_collection",
    url="http://localhost:6333"
)
- After this step, the document has been converted into searchable vector data.

# Step6: User Asks a Question
- When the user sends a question, the query API receives it:
@router.post("/")
async def query(question: str):

# Step7: Similarity Search
The application searches Qdrant using:
search_results = vector_db.similarity_search(
    query=question
)
- The purpose is to retrieve the pieces of the document that are most relevant to the question.(This is the Retrieval part of RAG.)

# Step8: Create Context
- After retrieving the relevant chunks, the application combines them into a context:
context = "\n\n".join(
    [
        f"[Page {result.metadata.get('page', 'unknown')}] {result.page_content}"
        for result in search_results
    ]
)

# Step9: Give Context to Gemini
- The application creates a system prompt containing the retrieved context:
system_prompt = f"""
You are a helpful assistant that answers questions based on
the provided context.

If the context does not contain the answer,
respond with "I don't know."

Context:
{context}
"""
- Then the question and context are sent to the Gemini chat.

# Diference between Embedding Model VS Chat Model
- These are Gemini Related Components.
(A)  Embedding Model
GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)
- Convert text into vectors for semantic search.

(B) Chat Model
ChatGoogleGenerativeAI(
    model="gemini-3.8-flash"
)
- Generate the final natural-language answer.

# Difference Between RAG VS Fine Tunning
- RAG = RAG gives the model relevant information at query time.
- Fine Tunning = Fine-tuning changes the model's learned behavior/parameters by training
it further on examples.

# Project Explnation:
My project is a basic Retrieval-Augmented Generation (RAG)
application. I load a PDF using PyPDFLoader, split the document into
smaller chunks using RecursiveCharacterTextSplitter, generate
embeddings for those chunks using Google's embedding model, and store
the vectors in Qdrant. When a user asks a question through the FastAPI
endpoint, the application performs a similarity search against the
Qdrant collection and retrieves relevant document chunks. These chunks
are combined into a context and passed to the Gemini chat model along
with the user's question. Gemini then generates the final answer based
on the retrieved context.

# One-Line Architecture
PDF → Chunks → Embeddings → Qdrant (database) → Similarity Search → Context → Gemini → Answer

# Q1. Why did you use Qdrant?
I used Qdrant as a vector database to store document embeddings and efficiently retrieve chunks that are semantically similar to the user's query.

# Q2. Why embeddings?
Embeddings convert text into numerical vector representations that capture semantic meaning, allowing us to perform similarity-based retrieval.

# Q3. Why chunking?
Large documents are divided into smaller chunks so that retrieval can return focused and relevant pieces of information instead of passing the entire document to the LLM. Chunking also helps manage context size and improves retrieval quality.

# Q4. What is chunk overlap?
Chunk overlap means neighboring chunks share some content. It helps preserve context when important information falls near a chunk boundary.

# Q5. What is LangChain?
LangChain is a framework that provides components and abstractions for building LLM applications, including document loaders, text splitters, embeddings, vector stores, retrievers and LLM integrations.


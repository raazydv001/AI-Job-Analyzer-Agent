import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIRECTORY = BASE_DIR / "data" / "chroma_db"

COLLECTION_NAME = "resume_collection"


# ============================================================
# CREATE EMBEDDING MODEL
# ============================================================

def create_embedding_model():

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is missing."
        )

    return OpenAIEmbeddings(
        model="openai/text-embedding-3-small",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )


# ============================================================
# SPLIT RESUME TEXT
# ============================================================

def split_resume_text(
    resume_text: str,
    filename: str
):

    if not resume_text.strip():
        raise ValueError(
            "Resume text is empty."
        )

    document = Document(
        page_content=resume_text,
        metadata={
            "source": filename,
            "document_type": "resume"
        }
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=80,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = text_splitter.split_documents(
        [document]
    )

    for index, chunk in enumerate(
        chunks,
        start=1
    ):
        chunk.metadata["chunk_id"] = index

    return chunks


# ============================================================
# CREATE CHROMA DATABASE
# ============================================================

def create_resume_vector_store(chunks):

    if not chunks:
        raise ValueError(
            "No resume chunks were created."
        )

    CHROMA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    embeddings = create_embedding_model()

    # Delete previous resume collection
    try:
        old_db = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DIRECTORY)
        )

        old_db.delete_collection()

    except Exception:
        pass


    # Create fresh collection
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIRECTORY),
        collection_metadata={
            "hnsw:space": "cosine"
        }
    )

    return vector_db


# ============================================================
# LOAD CHROMA DATABASE
# ============================================================

def load_resume_vector_store():

    if not CHROMA_DIRECTORY.exists():
        raise ValueError(
            "Resume vector database does not exist. "
            "Build Resume RAG first."
        )

    embeddings = create_embedding_model()

    vector_db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIRECTORY)
    )

    return vector_db


# ============================================================
# CREATE RETRIEVER
# ============================================================

def create_resume_retriever(k=3):

    vector_db = load_resume_vector_store()

    retriever = vector_db.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k
        }
    )

    return retriever


# ============================================================
# SEARCH RESUME
# ============================================================

def search_resume(
    query: str,
    k: int = 3
):

    if not query.strip():
        raise ValueError(
            "Search query cannot be empty."
        )

    vector_db = load_resume_vector_store()

    results = vector_db.similarity_search_with_score(
        query,
        k=k
    )

    return results
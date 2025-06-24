import os
import platform
import chromadb
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
import argparse
from knowledge_manager import knowledge_hub

def index_codebase(include_docs=None, include_external=None, reindex=False):
    """
    Index codebase for RAG system

    Args:
        include_docs: path to documentation directory
        include_external: URL for external documentation
        reindex: whether to reindex existing collections
    """
    print(f"Indexing codebase{'with docs' if include_docs else ''}...")

    # Platform-adaptive embedding function
    embedding_fn = OllamaEmbeddingFunction(
        model_name="nomic-embed-text",
        url="http://localhost:11434" if platform.system() == "Darwin" else "http://ollama:11434"
    )

    client = chromadb.PersistentClient(path="./chroma_db")

    # Delete collection if reindexing
    if reindex and "codebase" in client.list_collections():
        client.delete_collection("codebase")

    collection = client.get_or_create_collection(
        "codebase",
        embedding_function=embedding_fn
    )

    # Index code files
    project_src = os.path.join(
        os.getenv("VUE_PROJECT_DIR", os.path.expanduser("~/vue-project")),
        "src"
    )
    loader = DirectoryLoader(
        project_src,
        glob="**/*.{vue,ts,js,md}"
    )

    docs = loader.load()

    # Index documentation if provided
    if include_docs:
        docs_loader = DirectoryLoader(
            include_docs,
            glob="**/*.{md,pdf,txt}"
        )
        docs.extend(docs_loader.load())

    # Process external documentation (simplified for now)
    if include_external:
        from langchain_community.document_loaders import WebBaseLoader
        web_loader = WebBaseLoader(include_external)
        docs.extend(web_loader.load())

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(docs)

    # Add to collection
    collection.add(
        documents=[doc.page_content for doc in chunks],
        metadatas=[doc.metadata for doc in chunks],
        ids=[f"id_{i}" for i in range(len(chunks))]
    )

    # Index resources using KnowledgeHub
    knowledge_hub.index_resource(project_src, "code")

    print(f"Indexed {len(chunks)} code/documentation chunks")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Index codebase for RAG system')
    parser.add_argument('--include-docs', help='Path to documentation directory')
    parser.add_argument('--include-external', help='URL for external documentation')
    parser.add_argument('--reindex', action='store_true', help='Reindex existing collections')
    args = parser.parse_args()

    index_codebase(args.include_docs, args.include_external, args.reindex)

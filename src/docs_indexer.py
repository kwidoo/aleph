import requests
from bs4 import BeautifulSoup
import markdown
import platform
from langchain.document_loaders import WebBaseLoader, PDFMinerLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import os
import argparse

class ExternalDocIndexer:
    def __init__(self):
        """Initialize document indexer"""
        # Configure for different platforms
        CHROMA_HOST = "localhost" if platform.system() == "Darwin" else "chromadb"

        self.client = chromadb.HttpClient(host=CHROMA_HOST, port=8000)
        self.collection = self.client.get_or_create_collection("external_docs")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            separators=["\n\n", "\n", " ", ""]
        )

    def index_vue_docs(self):
        """Index Vue.js documentation"""
        print("Indexing Vue.js documentation...")
        loader = WebBaseLoader([
            "https://vuejs.org/guide/introduction",
            "https://vuejs.org/guide/typescript/overview",
            "https://vuejs.org/api/composition-api",
            "https://vuejs.org/guide/components/props"
        ])
        docs = loader.load()
        chunks = self.splitter.split_documents(docs)
        self._add_to_collection(chunks, "vue")
        print(f"Added {len(chunks)} Vue.js documentation chunks")

    def index_tailwind_docs(self):
        """Index Tailwind CSS documentation"""
        print("Indexing Tailwind CSS documentation...")
        loader = WebBaseLoader([
            "https://tailwindcss.com/docs/installation",
            "https://tailwindcss.com/docs/responsive-design",
            "https://tailwindcss.com/docs/flex",
            "https://tailwindcss.com/docs/grid-template-columns"
        ])
        docs = loader.load()
        chunks = self.splitter.split_documents(docs)
        self._add_to_collection(chunks, "tailwind")
        print(f"Added {len(chunks)} Tailwind CSS documentation chunks")

    def index_custom_docs(self, paths):
        """Index local documentation files"""
        print("Indexing custom documentation...")
        for path in paths:
            if path.endswith(".md"):
                with open(path, 'r') as f:
                    content = f.read()
                    html = markdown.markdown(content)
                    soup = BeautifulSoup(html, 'html.parser')
                    text = soup.get_text()
                    chunks = self.splitter.split_text(text)
                    self._add_to_collection(
                        [{"page_content": chunk, "metadata": {"source": path}} for chunk in chunks],
                        "custom"
                    )
            elif path.endswith(".pdf"):
                loader = PDFMinerLoader(path)
                docs = loader.load()
                chunks = self.splitter.split_documents(docs)
                self._add_to_collection(chunks, "custom")
        print("Custom documentation indexed")

    def _add_to_collection(self, chunks, doc_type):
        """Add chunks to collection"""
        for i, chunk in enumerate(chunks):
            try:
                if isinstance(chunk, dict):
                    self.collection.add(
                        documents=[chunk["page_content"]],
                        metadatas=[{"source": chunk["metadata"].get("source", "unknown"), "type": doc_type}],
                        ids=[f"{doc_type}_{i}"]
                    )
                else:
                    self.collection.add(
                        documents=[chunk.page_content],
                        metadatas=[{"source": chunk.metadata.get("source", "unknown"), "type": doc_type}],
                        ids=[f"{doc_type}_{i}"]
                    )
            except Exception as e:
                print(f"Error adding document: {e}")

    def query_docs(self, question, n_results=3):
        """Query documentation"""
        return self.collection.query(
            query_texts=[question],
            n_results=n_results
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Index external documentation')
    parser.add_argument('--vue', action='store_true', help='Index Vue.js docs')
    parser.add_argument('--tailwind', action='store_true', help='Index Tailwind CSS docs')
    parser.add_argument('--custom', nargs='+', help='Custom documentation files')
    args = parser.parse_args()

    indexer = ExternalDocIndexer()

    if args.vue:
        indexer.index_vue_docs()

    if args.tailwind:
        indexer.index_tailwind_docs()

    if args.custom:
        indexer.index_custom_docs(args.custom)

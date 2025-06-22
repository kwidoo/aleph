import chromadb
from chromadb.utils.embedding_functions import MultiModalEmbeddingFunction
import requests
from PIL import Image
import io

class KnowledgeHub:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./knowledge_db")
        self.text_embedder = OllamaEmbeddingFunction(model="nomic-embed-text")
        self.image_embedder = MultiModalEmbeddingFunction()

        self.collections = {
            "code": self.client.get_or_create_collection("code", embedding_function=self.text_embedder),
            "docs": self.client.get_or_create_collection("docs", embedding_function=self.text_embedder),
            "designs": self.client.get_or_create_collection("designs", embedding_function=self.image_embedder),
            "decisions": self.client.get_or_create_collection("decisions", embedding_function=self.text_embedder)
        }

    def index_resource(self, resource_path, resource_type):
        if resource_type == "code":
            self._index_code(resource_path)
        elif resource_type == "markdown":
            self._index_markdown(resource_path)
        elif resource_type == "image":
            self._index_image(resource_path)
        elif resource_type == "meeting":
            self._index_meeting_transcript(resource_path)

    def _index_code(self, file_path):
        with open(file_path, "r") as f:
            content = f.read()
        self.collections["code"].add(
            documents=[content],
            metadatas=[{"path": file_path, "language": file_path.split(".")[-1]}],
            ids=[file_path]
        )

    def _index_markdown(self, file_path):
        pass

    def _index_image(self, image_path):
        if image_path.startswith("http"):
            response = requests.get(image_path)
            image = Image.open(io.BytesIO(response.content))
        else:
            image = Image.open(image_path)

        self.collections["designs"].add(
            images=[image],
            metadatas=[{"source": image_path}],
            ids=[image_path]
        )

    def _index_meeting_transcript(self, transcript_path):
        pass

    def query(self, query, modality="text", n_results=5):
        if modality == "text":
            return self.collections["code"].query(query_texts=[query], n_results=n_results)
        elif modality == "image":
            return self.collections["designs"].query(query_images=[query], n_results=n_results)
        elif modality == "multimodal":
            pass

    def generate_knowledge_graph(self):
        pass

knowledge_hub = KnowledgeHub()

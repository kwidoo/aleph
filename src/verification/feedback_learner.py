import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

class VerificationFeedback:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./verification_db")
        self.embedding_fn = OllamaEmbeddingFunction(model="nomic-embed-text")
        self.collection = self.client.get_or_create_collection(
            "verification_feedback",
            embedding_function=self.embedding_fn
        )

    def record_verification(self, report):
        """Store verification results for learning"""
        feedback_id = f"feedback_{report['id']}"
        self.collection.add(
            documents=[json.dumps(report)],
            ids=[feedback_id],
            metadatas={
                "score": report["verification_score"],
                "verified": report["verified"],
                "timestamp": report["timestamp"]
            }
        )

    def get_similar_feedback(self, requirements, n=3):
        """Find similar verification cases"""
        results = self.collection.query(
            query_texts=[json.dumps(requirements)],
            n_results=n
        )
        return [
            {"metadata": m, "document": d}
            for m, d in zip(results["metadatas"][0], results["documents"][0])
        ]

    def improve_generation(self, requirements):
        """Use historical feedback to improve generation"""
        similar = self.get_similar_feedback(requirements)
        feedback_context = "\n".join([item["document"] for item in similar])

        prompt = f"""
        Generate better Vue component code by learning from past verification feedback:

        Requirements:
        {requirements}

        Past Feedback:
        {feedback_context}

        Apply lessons learned to avoid previous mistakes.
        """
        return self.c.complete(prompt, max_tokens=1500)

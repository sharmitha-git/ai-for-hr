import os
import chromadb


os.makedirs(
    "data/chroma_db",
    exist_ok=True
)


client = chromadb.PersistentClient(
    path="data/chroma_db"
)


candidate_collection = (
    client.get_or_create_collection(
        name="candidate_embeddings"
    )
)


job_collection = (
    client.get_or_create_collection(
        name="job_embeddings"
    )
)


class ChromaService:


    # =====================================
    # Store Candidate Embedding
    # =====================================

    @staticmethod
    def store_candidate_embedding(

        candidate_id,
        embedding,
        metadata
    ):

        candidate_collection.add(

            ids=[str(candidate_id)],

            embeddings=[embedding],

            metadatas=[metadata]
        )


    # =====================================
    # Store Job Embedding
    # =====================================

    @staticmethod
    def store_job_embedding(

        job_id,
        embedding,
        metadata
    ):

        job_collection.add(

            ids=[str(job_id)],

            embeddings=[embedding],

            metadatas=[metadata]
        )


    # =====================================
    # Get All Candidate Embeddings
    # =====================================

    @staticmethod
    def get_all_candidate_embeddings():

        return candidate_collection.get(
            include=[
                "embeddings",
                "metadatas"
            ]
        )


    # =====================================
    # Get Job Embedding
    # =====================================

    @staticmethod
    def get_job_embedding(
        job_id
    ):

        return job_collection.get(

            ids=[str(job_id)],

            include=[
                "embeddings",
                "metadatas"
            ]
        )
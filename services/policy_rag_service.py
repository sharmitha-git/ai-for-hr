from langchain_community.document_loaders import (
    PyPDFLoader
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_openai import (
    OpenAIEmbeddings
)

from langchain_community.vectorstores import (
    FAISS
)

import os


POLICY_DB_PATH = (
    "memory/policy_faiss"
)

RETRIEVAL_SOURCE = "policy_faiss"

# L2 distance from FAISS; lower is a closer match.
LOW_CONFIDENCE_DISTANCE = 1.15


def _distance_to_confidence(distance: float) -> float:
    """Map vector distance to a 0-1 confidence score."""

    return max(
        0.0,
        min(1.0, 1.0 - (float(distance) / 1.5)),
    )


def ingest_policy_documents():

    documents = []

    policy_folder = (
        "data/policies"
    )

    if not os.path.isdir(
        policy_folder
    ):

        return 0

    for file in os.listdir(
        policy_folder
    ):

        if file.endswith(".pdf"):

            loader = PyPDFLoader(

                os.path.join(
                    policy_folder,
                    file
                )
            )

            docs = loader.load()

            for doc in docs:

                doc.metadata["source_file"] = file

            documents.extend(docs)

    if not documents:

        return 0

    splitter = (
        RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    )

    chunks = splitter.split_documents(
        documents
    )

    embeddings = OpenAIEmbeddings()

    vectordb = FAISS.from_documents(

        chunks,
        embedding=embeddings
    )

    os.makedirs(
        POLICY_DB_PATH,
        exist_ok=True
    )

    vectordb.save_local(
        POLICY_DB_PATH
    )

    return len(chunks)


def search_policy_documents(
    query,
    k=3,
):
    """
    Retrieve policy chunks with similarity scores and confidence metadata.
    """

    empty_payload = {
        "results": [],
        "chunks": [],
        "retrieval_source": RETRIEVAL_SOURCE,
        "retrieval_confidence": 0.0,
        "low_confidence": True,
        "policy_chunks_used": [],
    }

    if not os.path.isdir(
        POLICY_DB_PATH
    ):

        return empty_payload

    embeddings = OpenAIEmbeddings()

    try:

        vectordb = FAISS.load_local(

            POLICY_DB_PATH,

            embeddings,

            allow_dangerous_deserialization=True
        )

        scored_docs = vectordb.similarity_search_with_score(

            query,

            k=k
        )

    except Exception:

        return empty_payload

    chunks = []
    legacy_results = []

    for doc, distance in scored_docs:

        confidence = _distance_to_confidence(
            distance
        )
        source_file = doc.metadata.get(
            "source_file",
            "policy_pdf"
        )

        chunk = {
            "text": doc.page_content,
            "source": source_file,
            "distance": float(distance),
            "confidence": confidence,
        }
        chunks.append(chunk)

        legacy_results.append(
            f"Source: {source_file} | "
            f"{doc.page_content}"
        )

    if not chunks:

        return empty_payload

    top_confidence = max(
        c["confidence"] for c in chunks
    )
    low_confidence = (
        top_confidence < _distance_to_confidence(
            LOW_CONFIDENCE_DISTANCE
        )
        or chunks[0]["distance"] > LOW_CONFIDENCE_DISTANCE
    )

    return {
        "results": legacy_results,
        "chunks": chunks,
        "retrieval_source": RETRIEVAL_SOURCE,
        "retrieval_confidence": round(
            top_confidence,
            3,
        ),
        "low_confidence": low_confidence,
        "policy_chunks_used": [
            {
                "source": c["source"],
                "confidence": c["confidence"],
            }
            for c in chunks
        ],
    }


def search_policy_documents_legacy(query):
    """Backward-compatible string list return."""

    payload = search_policy_documents(query)
    return payload.get("results", [])

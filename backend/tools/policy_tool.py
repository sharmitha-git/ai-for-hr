from backend.tools.tool_registry import (
    register_tool
)

from services.policy_rag_service import (
    ingest_policy_documents as ingest_policy_documents_service,
    search_policy_documents as search_policy_documents_service,
)


@register_tool(
    "ingest_policy_documents"
)
def ingest_policy_documents():

    return {
        "chunks_indexed": (
            ingest_policy_documents_service()
        )
    }


@register_tool(
    "search_policy_documents"
)
def search_policy_documents(
    query
):

    return search_policy_documents_service(
        query
    )

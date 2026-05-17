"""
Grounded policy response generation with compliance guardrails.
"""

from backend.llm import llm

POLICY_SYSTEM_PROMPT = """
You are HireGuard AI's governance and compliance policy assistant.

STRICT RULES:
- Answer ONLY using the retrieved policy excerpts provided in the user message.
- Do NOT recommend, rank, or discuss specific candidates or hiring decisions.
- Do NOT invent policies, legal requirements, penalties, or procedures.
- If the excerpts do not support an answer, say the information is unavailable.
- Cite every substantive claim with [Source: <filename>] from the excerpts.
- Use a professional, enterprise-safe, compliance-focused tone.
- Do not speculate or provide legal advice beyond the excerpts.
""".strip()

NO_GROUNDED_POLICY_MESSAGE = (
    "No grounded policy information found.\n\n"
    "Retrieval confidence is below the required threshold or "
    "no relevant policy excerpts were returned.\n\n"
    "Next steps:\n"
    "- Upload or index governance PDFs in the Governance Console.\n"
    "- Rephrase your question with a specific policy topic "
    "(e.g., data retention, GDPR, sensitive data protection).\n"
    "- Contact your compliance officer for authoritative guidance."
)

NO_CHUNKS_MESSAGE = (
    "No grounded policy information found.\n\n"
    "No policy documents are indexed yet. "
    "Load governance PDFs and run policy indexing before "
    "asking compliance questions."
)

# Backward-compatible alias for tests/imports.
LOW_CONFIDENCE_MESSAGE = NO_GROUNDED_POLICY_MESSAGE


def format_chunks_for_prompt(chunks: list[dict]) -> str:

    blocks = []

    for index, chunk in enumerate(chunks, start=1):

        source = chunk.get("source", "policy_pdf")
        text = chunk.get("text", "")
        confidence = chunk.get("confidence", 0)

        blocks.append(
            f"[Excerpt {index}] [Source: {source}] "
            f"(retrieval confidence: {confidence:.2f})\n{text}"
        )

    return "\n\n".join(blocks)


def build_grounded_policy_response(
    query: str,
    chunks: list[dict],
    retrieval_confidence: float,
    low_confidence: bool,
) -> str:

    if low_confidence or not chunks:

        return NO_GROUNDED_POLICY_MESSAGE

    if retrieval_confidence <= 0:

        return NO_CHUNKS_MESSAGE

    context = format_chunks_for_prompt(chunks)

    user_prompt = f"""
User question:
{query}

Retrieved policy excerpts (use ONLY these):
{context}

Provide a concise governance/compliance answer.
If excerpts are insufficient for any part of the question, state that explicitly.
Do not mention candidates or recruiting recommendations.
"""

    try:

        response = llm.invoke(
            [
                {"role": "system", "content": POLICY_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ]
        )

        body = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

    except Exception:

        lines = [
            "Applicable Policy Guidance (retrieved excerpts only):\n"
        ]

        for index, chunk in enumerate(chunks, start=1):

            source = chunk.get("source", "policy_pdf")
            lines.append(
                f"{index}. [Source: {source}] {chunk.get('text', '')}"
            )
            lines.append("")

        body = "\n".join(lines).strip()

    footer = (
        f"\n\n---\n"
        f"Retrieval source: policy_faiss | "
        f"Overall confidence: {retrieval_confidence:.2f} | "
        f"Chunks used: {len(chunks)}"
    )

    return (body + footer).strip()

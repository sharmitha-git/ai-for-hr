from database.connection import SessionLocal

from backend.entities.conversation_memory import (
    ConversationMemory
)

# Partition keys — unrelated copilot flows must not share history.
MEMORY_SCOPE_AVAILABLE_JOBS = "available_jobs"
MEMORY_SCOPE_CANDIDATE_MATCHING = "candidate_matching"
MEMORY_SCOPE_GOVERNANCE = "governance"
MEMORY_SCOPE_OUTREACH = "outreach"

# Keep the five most recent user/assistant turns per scope (10 stored rows).
MAX_MEMORY_INTERACTIONS = 5
MAX_MEMORY_ENTRIES = MAX_MEMORY_INTERACTIONS * 2

# Supervisor route_type values mapped to a single memory partition.
_ROUTE_TYPE_TO_SCOPE = {
    "available_jobs": MEMORY_SCOPE_AVAILABLE_JOBS,
    "candidate_search": MEMORY_SCOPE_CANDIDATE_MATCHING,
    "shortlisted_candidates": MEMORY_SCOPE_CANDIDATE_MATCHING,
    "pending_candidates": MEMORY_SCOPE_CANDIDATE_MATCHING,
    "rejected_reasoning": MEMORY_SCOPE_CANDIDATE_MATCHING,
    "policy_lookup": MEMORY_SCOPE_GOVERNANCE,
    "pipeline_summary": MEMORY_SCOPE_GOVERNANCE,
    "governance_risks": MEMORY_SCOPE_GOVERNANCE,
    "email_outreach": MEMORY_SCOPE_OUTREACH,
}


def resolve_memory_scope(route_type):
    """
    Collapse granular supervisor routes into one of four memory buckets
    so recruiter/candidate history never bleeds into job-listing queries.
    """

    if not route_type:

        return MEMORY_SCOPE_CANDIDATE_MATCHING

    return _ROUTE_TYPE_TO_SCOPE.get(
        route_type,
        MEMORY_SCOPE_CANDIDATE_MATCHING
    )


def _prune_scoped_memory(
    db,
    session_id,
    memory_scope
):

    # Drop oldest rows beyond the interaction window for this scope only.
    scoped_entries = (
        db.query(ConversationMemory)
        .filter(
            ConversationMemory.session_id == session_id,
            ConversationMemory.memory_scope == memory_scope,
        )
        .order_by(
            ConversationMemory.created_at.desc(),
            ConversationMemory.id.desc(),
        )
        .all()
    )

    if len(scoped_entries) <= MAX_MEMORY_ENTRIES:

        return

    for stale_entry in scoped_entries[MAX_MEMORY_ENTRIES:]:

        db.delete(stale_entry)


def add_memory(
    session_id,
    role,
    message,
    memory_scope
):

    db = SessionLocal()

    try:

        memory_entry = ConversationMemory(
            session_id=session_id,
            role=role,
            message=message,
            memory_scope=memory_scope,
        )

        db.add(memory_entry)
        db.commit()

        _prune_scoped_memory(
            db,
            session_id,
            memory_scope
        )
        db.commit()

    finally:

        db.close()


def get_memory(
    session_id,
    memory_scope
):

    db = SessionLocal()

    try:

        # Only rows for this partition — legacy NULL scope rows are ignored
        # so pre-migration candidate history cannot leak into job listings.
        memory_entries = (
            db.query(ConversationMemory)
            .filter(
                ConversationMemory.session_id == session_id,
                ConversationMemory.memory_scope == memory_scope,
            )
            .order_by(
                ConversationMemory.created_at,
                ConversationMemory.id,
            )
            .limit(MAX_MEMORY_ENTRIES)
            .all()
        )

        if not memory_entries:

            return ""

        return "\n".join(
            f"{entry.role}: {entry.message}"
            for entry in memory_entries
            if entry.message
        )

    finally:

        db.close()

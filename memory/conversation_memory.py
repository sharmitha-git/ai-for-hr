conversation_store = {}


def get_memory(session_id):

    if session_id not in conversation_store:

        conversation_store[session_id] = []

    return conversation_store[session_id]


def add_memory(
    session_id,
    role,
    content
):

    if session_id not in conversation_store:

        conversation_store[session_id] = []

    conversation_store[session_id].append({

        "role": role,
        "content": content
    })
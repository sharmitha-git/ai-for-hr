from langchain_openai import ChatOpenAI

from dotenv import load_dotenv


load_dotenv()


llm = ChatOpenAI(
    temperature=0
)


def supervisor_agent(state):

    query = state["query"]

    prompt = f"""
    You are an AI orchestration supervisor for a
    human-in-the-loop hiring platform.

    Available agents:

    1. recruiter
       - candidate search
       - resume matching
       - advisory hiring recommendations
       - skill evaluation

    2. governance
       - governance risks
       - compliance
       - audit
       - explainability
        - candidate risk analysis

    3. operations
       - general platform operations
       - workflow questions
       - hiring pipeline status
       - scheduling
       - email workflows

    User Query:
    {query}

    Return ONLY ONE agent name.

    Never assume AI can make a final
    shortlist or rejection decision.

    Valid outputs:
    recruiter
    governance
    operations
    """

    response = llm.invoke(
        prompt
    )

    selected_agent = (
        response.content
        .strip()
        .lower()
    )

    if selected_agent not in [

        "recruiter",
        "governance",
        "operations"
    ]:

        selected_agent = (
            "operations"
        )

    state["selected_agent"] = (
        selected_agent
    )

    return state

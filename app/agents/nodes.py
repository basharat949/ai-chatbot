from langchain.messages import AIMessage

from app.agents.state import CryptoAgentState


async def generate_answer(
    state: CryptoAgentState,
) -> dict:
    """
    Temporary answer-generation node.

    Current responsibility:
    - Read the user's original query from graph state.
    - Generate a temporary assistant response.
    - Append an AIMessage to the messages state.

    Later this node will call Gemini or Groq through
    the configured LLM provider.
    """

    original_query = state["original_query"]

    response = (
        "Hello! I am CryptoMind AI. "
        f"I received your question: {original_query}. "
        "This is a temporary LangGraph response. "
    )

    return {
        "messages": [
            AIMessage(content=response),
        ],
    }
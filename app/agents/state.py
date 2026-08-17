from langgraph.graph import MessagesState


class CryptoAgentState(MessagesState):
    """
    Shared state for the CryptoMind AI LangGraph workflow.

    MessagesState already provides:
        messages: list[AnyMessage]
    """

    user_id: int
    chat_id: int
    original_query: str
    token_symbol: str | None
    coingecko_id: str | None

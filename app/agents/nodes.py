from langchain_core.messages import (
    AIMessage,
    SystemMessage,
)

from app.agents.state import CryptoAgentState
from app.llms.provider import get_llm


SYSTEM_PROMPT = """
You are CryptoMind AI, an evidence-focused cryptocurrency research assistant.

Your responsibilities:
- Explain crypto and blockchain concepts clearly.
- Distinguish facts from assumptions.
- Never guarantee profits or financial returns.
- State when current market data or external evidence is unavailable.
- Keep the response useful, accurate, and professionally structured.

At this stage, you do not have live market tools or document retrieval.
Do not pretend that you accessed live prices, news, whitepapers, or external sources.
"""


async def generate_answer(
    state: CryptoAgentState,
) -> dict:
    llm = get_llm()

    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]
    )

    if not isinstance(response, AIMessage):
        raise RuntimeError(
            "Gemini did not return a valid AIMessage"
        )

    return {
        "messages": [response],
    }
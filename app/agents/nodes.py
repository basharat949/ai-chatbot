import re

from langchain_core.messages import (
    AIMessage,
    SystemMessage,
)

from app.agents.state import CryptoAgentState
from app.data.supported_tokens import SUPPORTED_TOKENS
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

TOKEN_PATTERN = re.compile(
    rf"(?<!\w)(?:{'|'.join(re.escape(alias) for alias in SUPPORTED_TOKENS)})(?!\w)",
    flags=re.IGNORECASE,
)


def resolve_token(
    state: CryptoAgentState,
) -> dict:
    query = state["original_query"]
    match = TOKEN_PATTERN.search(query)

    if match is None:
        return {
            "token_symbol": None,
            "coingecko_id": None,
        }

    token_symbol, coingecko_id = SUPPORTED_TOKENS[
        match.group().lower()
    ]

    return {
        "token_symbol": token_symbol,
        "coingecko_id": coingecko_id,
    }


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

from langgraph.graph import END, START, StateGraph

from app.agents.nodes import generate_answer
from app.agents.state import CryptoAgentState


def build_crypto_agent():
    """
    Build and compile the initial CryptoMind AI graph.

    Current workflow:
        START -> generate_answer -> END
    """

    graph_builder = StateGraph(CryptoAgentState)

    graph_builder.add_node(
        "generate_answer",
        generate_answer,
    )

    graph_builder.add_edge(
        START,
        "generate_answer",
    )

    graph_builder.add_edge(
        "generate_answer",
        END,
    )

    return graph_builder.compile()


crypto_agent = build_crypto_agent()
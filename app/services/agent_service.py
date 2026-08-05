from langchain.messages import AIMessage, HumanMessage

from app.agents.graph import crypto_agent


class AgentService:
    """Provide the application-facing interface to the compiled AI workflow."""

    @staticmethod
    async def run(
        *,
        user_id: int,
        chat_id: int,
        query: str,
    ) -> str:
        """Run the LangGraph workflow and return its final assistant response."""

        result = await crypto_agent.ainvoke(
            {
                "messages": [
                    HumanMessage(content=query),
                ],
                "user_id": user_id,
                "chat_id": chat_id,
                "original_query": query,
            }
        )

        messages = result["messages"]

        if not messages:
            raise RuntimeError(
                "Agent completed without returning any messages"
            )

        final_message = messages[-1]

        if not isinstance(final_message, AIMessage):
            raise RuntimeError(
                "Agent did not return a valid assistant message"
            )

        if not isinstance(final_message.content, str):
            raise RuntimeError(
                "Assistant response content must be a string"
            )

        return final_message.content

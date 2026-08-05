from langchain.messages import AIMessage, HumanMessage

from app.agents.graph import crypto_agent


class AgentService:
    @staticmethod
    async def run(
        *,
        user_id: int,
        chat_id: int,
        query: str,
    ) -> str:
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

        assistant_text = final_message.text

        if not assistant_text.strip():
            raise RuntimeError(
                "Agent returned an empty assistant response"
            )

        return assistant_text
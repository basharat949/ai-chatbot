from fastapi import FastAPI

from app.api.routes import auth, users, chats, messages

app = FastAPI(title="AI Chatbot Backend")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(chats.router)
app.include_router(messages.router)


@app.get("/health")
async def health_check():
    """Report whether the API process is available to serve requests."""

    return {"status": "healthy"}

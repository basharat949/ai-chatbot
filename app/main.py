from fastapi import FastAPI

from app.api.routes import auth, users

app = FastAPI(title="AI Chatbot Backend")

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
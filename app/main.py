from fastapi import FastAPI

app = FastAPI(
    title="AI Chatbot Backend",
    version="1.0.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "AI Chatbot Backend is running",
    }
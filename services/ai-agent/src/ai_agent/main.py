from fastapi import FastAPI

app = FastAPI(title="ai-agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-agent"}

from fastapi import FastAPI

app = FastAPI(title="Amazon Commerce Agent")


@app.get("/health")
async def health():
    return {"status": "ok"}

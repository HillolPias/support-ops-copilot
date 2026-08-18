from fastapi import FastAPI

app = FastAPI(title="Support Ops Copilot")


@app.get("/health")
def health_check():
    return {"ok": True}

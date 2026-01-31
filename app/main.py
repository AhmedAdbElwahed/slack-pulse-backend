from fastapi import FastAPI
from app.api.v1.task import router as task_router
from app.api.v1.websockets import router as websocket_router


app = FastAPI(title="Pulse API")

app.include_router(task_router, prefix="/api/v1", tags=["tasks"])
app.include_router(websocket_router, tags=["websockets"])


@app.get("/")
def read_root():
    return {"status": "Pulse Backend is Online"}

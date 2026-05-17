from fastapi import FastAPI
from pydantic import BaseModel
from celery.result import AsyncResult
from celery_app import celery as celery_app
import tasks

app = FastAPI(
    title="Health Check Service",
    description="A minimal FastAPI app with a health check endpoint and Celery tasks.",
    version="0.1.0",
)


@app.get("/health", summary="Health check", tags=["Health"])
def health_check() -> dict:
    """Return a simple health status response."""
    return {"status": "healthy, it is running perfectly fine!"}


class AddRequest(BaseModel):
    x: int
    y: int


@app.post("/tasks/add", summary="Create add task", tags=["Tasks"])
def create_add_task(req: AddRequest):
    """Create a Celery task that adds two numbers and return task id."""
    task = tasks.add.delay(req.x, req.y)
    return {"task_id": task.id}


@app.get("/tasks/{task_id}", summary="Get task status", tags=["Tasks"])
def get_task_status(task_id: str):
    """Return Celery task status and result (if ready)."""
    ar = AsyncResult(task_id, app=celery_app)
    return {"task_id": task_id, "status": ar.status, "result": ar.result}

@app.get("/hello-world", summary="Hello World", tags=["General"])
def hello_world() -> dict:
    """Return a simple hello world response."""
    return {"message": "Hello, World!"}

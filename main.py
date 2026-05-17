from fastapi import FastAPI

app = FastAPI(
    title="Health Check Service",
    description="A minimal FastAPI app with a health check endpoint.",
    version="0.1.0",
)


@app.get("/health", summary="Health check", tags=["Health"])
def health_check() -> dict:
    """Return a simple health status response."""
    return {"status": "healthy, it is running perfectly fine!"}

@app.get("/hello-world", summary="Hello World", tags=["General"])
def hello_world() -> dict:
    """Return a simple hello world response."""
    return {"message": "Hello, World!"}

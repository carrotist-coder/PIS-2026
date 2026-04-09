"""Main FastAPI application entry point."""

from fastapi import FastAPI
from src.infrastructure.adapter.inbound.fastapi_deal_controller import router

app = FastAPI(title="Deal Service API", version="1.0")

app.include_router(router)


@app.get("/health")
def health_check():
  return {"status": "ok"}

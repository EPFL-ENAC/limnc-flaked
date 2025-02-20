from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from logging import basicConfig, INFO, DEBUG
from pydantic import BaseModel
from .views.scheduler import router as scheduler_router
from .views.config import router as config_router

basicConfig(level=DEBUG)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""
    status: str = "OK"


@app.get(
    "/healthz",
    tags=["Healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
async def get_health(
) -> HealthCheck:
    """
    Endpoint to perform a healthcheck on for kubenernetes liveness and
    readiness probes.
    """
    return HealthCheck(status="OK")

app.include_router(
    scheduler_router,
    prefix="/scheduler",
    tags=["Scheduler"],
)

app.include_router(
    config_router,
    prefix="/config",
    tags=["Config"],
)
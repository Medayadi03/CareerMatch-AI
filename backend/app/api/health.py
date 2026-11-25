from typing import Literal

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/health", tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["alive", "ready", "not_ready"]


@router.get("/live", response_model=HealthResponse)
def live() -> HealthResponse:
    return HealthResponse(status="alive")


@router.get("/ready", response_model=HealthResponse, responses={503: {"model": HealthResponse}})
def ready(request: Request, response: Response) -> HealthResponse:
    # Phase 0 serves no business data: no external dependency is required.
    if not request.app.state.ready:
        response.status_code = 503
        return HealthResponse(status="not_ready")
    return HealthResponse(status="ready")

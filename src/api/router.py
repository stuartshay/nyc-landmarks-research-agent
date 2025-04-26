"""
Main API router module for the NYC Landmarks Research Agent.
Sets up routing for research and landmark endpoints.
"""

from fastapi import APIRouter

from src.endpoints.research import router as research_router

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    research_router,
    prefix="/research",
    tags=["research"],
)

# Additional endpoint routers can be included here
# For example:
# api_router.include_router(
#     landmarks_router,
#     prefix="/landmarks",
#     tags=["landmarks"],
# )

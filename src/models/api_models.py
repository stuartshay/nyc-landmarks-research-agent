"""
API models for the NYC Landmarks Research Agent.
Defines request and response structures using Pydantic.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error details")
    status_code: int = Field(..., description="HTTP status code")


class SourceDocument(BaseModel):
    """Source document for research with metadata."""

    source_id: str = Field(..., description="Unique identifier for the source")
    source_type: str = Field(..., description="Type of source (e.g., 'pdf', 'api')")
    title: Optional[str] = Field(None, description="Title or name of the source")
    content: str = Field(..., description="Relevant content from the source")
    page: Optional[int] = Field(None, description="Page number for PDF sources")
    relevance_score: Optional[float] = Field(None, description="Relevance score for the source")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")


class LandmarkImage(BaseModel):
    """Image of a landmark with metadata."""

    url: HttpUrl = Field(..., description="URL to the image")
    caption: Optional[str] = Field(None, description="Caption or description of the image")
    year: Optional[int] = Field(None, description="Year the image was taken")
    source: Optional[str] = Field(None, description="Source of the image")
    is_historical: bool = Field(False, description="Whether this is a historical image")


class ResearchRequest(BaseModel):
    """Request model for generating landmark research."""

    query: str = Field(
        ...,
        description="Research question or topic",
        min_length=5,
        max_length=1000,
        examples=["Tell me about the history of the Flatiron Building"],
    )
    conversation_id: Optional[str] = Field(None, description="ID for continuing a conversation")
    landmark_id: Optional[str] = Field(None, description="Specific landmark ID to focus on (e.g., LP-00001)")
    include_images: bool = Field(True, description="Whether to include images in the response")
    max_sources: int = Field(5, description="Maximum number of sources to include", ge=1, le=20)

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "query": "What's the architectural significance of the Flatiron Building?",
                "conversation_id": None,
                "landmark_id": "LP-00004",
                "include_images": True,
                "max_sources": 5,
            }
        }


class ResearchResponse(BaseModel):
    """Response model for landmark research."""

    conversation_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Conversation ID for follow-up questions",
    )
    query: str = Field(..., description="Original research question or topic")
    report: str = Field(..., description="Generated research report content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of generation")
    images: Optional[List[LandmarkImage]] = Field([], description="Images related to the landmark")
    sources: Optional[List[SourceDocument]] = Field([], description="Source documents used for the research")
    landmark_id: Optional[str] = Field(
        None,
        description="ID of the landmark if the report focuses on a specific landmark",
    )
    landmark_name: Optional[str] = Field(
        None,
        description="Name of the landmark if the report focuses on a specific landmark",
    )
    related_landmarks: Optional[List[Dict[str, str]]] = Field(
        [], description="List of related landmarks with their IDs and names"
    )
    suggested_queries: Optional[List[str]] = Field(
        [], description="Suggested follow-up questions related to this research"
    )

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "query": "What's the architectural significance of the Flatiron Building?",
                "report": "The Flatiron Building, completed in 1902, is considered...",
                "timestamp": "2025-04-25T18:25:43.511Z",
                "landmark_id": "LP-00004",
                "landmark_name": "Flatiron Building",
                "images": [
                    {
                        "url": "https://example.com/flatiron.jpg",
                        "caption": "The Flatiron Building in 1903",
                        "year": 1903,
                        "source": "NYC Archives",
                        "is_historical": True,
                    }
                ],
                "sources": [
                    {
                        "source_id": "pdf-LP-00004-1",
                        "source_type": "pdf",
                        "title": "Flatiron Building Designation Report",
                        "content": "The Flatiron Building stands at the intersection of...",
                        "page": 2,
                        "relevance_score": 0.92,
                        "metadata": {
                            "author": "NYC Landmarks Preservation Commission",
                            "year": 1966,
                        },
                    }
                ],
                "related_landmarks": [{"id": "LP-00127", "name": "MetLife Tower"}],
                "suggested_queries": [
                    "Who was the architect of the Flatiron Building?",
                    "When was the Flatiron Building designated as a landmark?",
                ],
            }
        }

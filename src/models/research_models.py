"""
Research models for the NYC Landmarks Research Agent.
Defines internal data structures for research processing.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.models.landmark_models import LandmarkDetail, LandmarkPhoto


class SourcePassage(BaseModel):
    """A passage of text from a source document."""

    text: str = Field(..., description="The text content of the passage")
    source_id: str = Field(..., description="ID of the source document")
    source_title: Optional[str] = Field(None, description="Title of the source document")
    page_number: Optional[int] = Field(None, description="Page number for PDF sources")
    chunk_id: Optional[str] = Field(None, description="ID of the chunk within the source")
    relevance_score: float = Field(..., description="Relevance score of the passage to the query")
    landmark_id: Optional[str] = Field(None, description="ID of the landmark this passage relates to")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MemoryEntry(BaseModel):
    """An entry in the conversation memory."""

    conversation_id: str = Field(..., description="ID of the conversation")
    timestamp: datetime = Field(default_factory=datetime.now, description="Time when the entry was created")
    query: str = Field(..., description="User query")
    response: str = Field(..., description="Agent response")
    landmark_ids: List[str] = Field(default_factory=list, description="IDs of landmarks mentioned")
    landmark_names: List[str] = Field(default_factory=list, description="Names of landmarks mentioned")
    sources_used: List[Dict[str, Any]] = Field(default_factory=list, description="Sources used in the response")

    class Config:
        """Configure behavior."""

        arbitrary_types_allowed = True


class Conversation(BaseModel):
    """A conversation between a user and the research agent."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Conversation ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    entries: List[MemoryEntry] = Field(default_factory=list, description="Conversation entries")
    landmark_focus: Optional[str] = Field(None, description="ID of landmark focus if any")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ResearchContext(BaseModel):
    """Context for generating a research report."""

    query: str = Field(..., description="The user's query")
    conversation_id: Optional[str] = Field(None, description="ID of existing conversation")
    landmark_id: Optional[str] = Field(None, description="Specific landmark ID to focus on")
    relevant_passages: List[SourcePassage] = Field(default_factory=list, description="Relevant passages from sources")
    landmark_info: Optional[LandmarkDetail] = Field(None, description="Basic landmark information")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="Past conversation entries")
    images: List[LandmarkPhoto] = Field(default_factory=list, description="Images related to the landmark")


class ResearchTask(BaseModel):
    """A research task to be performed by the agent."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Task ID")
    query: str = Field(..., description="The research query")
    conversation_id: Optional[str] = Field(None, description="Conversation ID if this is part of a conversation")
    landmark_id: Optional[str] = Field(None, description="Specific landmark ID if focused on a landmark")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    status: str = Field("pending", description="Task status (pending, processing, completed, failed)")
    context: Optional[ResearchContext] = Field(None, description="Research context once assembled")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PromptTemplate(BaseModel):
    """Template for generating prompts for the language model."""

    name: str = Field(..., description="Name of the template")
    template: str = Field(..., description="The template string")
    description: str = Field(..., description="Description of when to use this template")

    def format(self, **kwargs) -> str:
        """Format the template with provided values."""
        return self.template.format(**kwargs)


# Standard prompt templates for the research agent
RESEARCH_PROMPT_TEMPLATE = PromptTemplate(
    name="landmark_research",
    description="Template for generating landmark research reports",
    template="""
You are an expert on New York City landmarks and architecture, tasked with creating a detailed research report
based on the following query: "{query}"

{system_instructions}

CONTEXT INFORMATION:
{context}

USER QUERY: {query}

Your response should be a well-structured, educational research report that:
1. Directly addresses the query with accurate information
2. Synthesizes information from multiple sources
3. Highlights architectural, historical, and cultural significance
4. Cites relevant passages when appropriate
5. Is formatted in clear paragraphs with appropriate headings
6. Uses a professional, educational tone suitable for a heritage organization

Respond with a comprehensive research report formatted in markdown.
""",
)

CONVERSATION_PROMPT_TEMPLATE = PromptTemplate(
    name="conversation_continuation",
    description="Template for continuing a research conversation",
    template="""
You are an expert on New York City landmarks and architecture, engaged in a conversation about NYC
landmarks. Your goal is to provide informative, accurate responses based on the available information.

CONVERSATION HISTORY:
{conversation_history}

CONTEXT INFORMATION:
{context}

NEW USER QUERY: {query}

Your response should:
1. Directly address the user's new query
2. Build upon information from the previous conversation when relevant
3. Provide new information and insights, not just repeat previous responses
4. Cite relevant passages when appropriate
5. Be formatted in clear paragraphs suitable for conversation
6. Maintain a helpful, professional tone

Respond with a comprehensive answer formatted in markdown.
""",
)

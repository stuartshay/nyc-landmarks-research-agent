"""
Research endpoints for the NYC Landmarks Research Agent.
Provides APIs for generating research reports about NYC landmarks.
"""

from fastapi import APIRouter, Depends, HTTPException

from src.clients.azure_openai_client import AzureOpenAIClient
from src.clients.landmark_metadata_client import LandmarkMetadataClient
from src.clients.vectorstore_client import VectorStoreClient
from src.models.api_models import ErrorResponse, ResearchRequest, ResearchResponse
from src.services.memory_service import MemoryService
from src.services.research_service import ResearchService

# Create router
router = APIRouter()


def get_research_service():
    """Dependency to get a configured ResearchService instance."""
    vector_client = VectorStoreClient()
    landmark_client = LandmarkMetadataClient()
    memory_service = MemoryService()
    openai_client = AzureOpenAIClient()

    return ResearchService(
        vector_client=vector_client,
        landmark_client=landmark_client,
        memory_service=memory_service,
        openai_client=openai_client,
    )


@router.post(
    "/generate",
    response_model=ResearchResponse,
    responses={
        200: {"description": "Research report generated successfully"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def generate_research(
    request: ResearchRequest,
    research_service: ResearchService = Depends(get_research_service),
):
    """
    Generate a research report about NYC landmarks based on the query.

    - **query**: The research question or topic
    - **conversation_id**: Optional ID for continuing a conversation
    - **landmark_id**: Optional specific landmark ID to focus the research on
    """
    try:
        result = await research_service.generate_report(
            query=request.query,
            conversation_id=request.conversation_id,
            landmark_id=request.landmark_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the exception here
        raise HTTPException(status_code=500, detail=f"Error generating research: {str(e)}")


@router.get("/conversations/{conversation_id}", response_model=list[ResearchResponse])
async def get_conversation_history(
    conversation_id: str,
    research_service: ResearchService = Depends(get_research_service),
):
    """
    Retrieve the history of a research conversation.

    - **conversation_id**: ID of the conversation to retrieve
    """
    try:
        history = await research_service.get_conversation_history(conversation_id)
        if not history:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        return history
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the exception here
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {str(e)}")


@router.delete("/conversations/{conversation_id}", response_model=dict)
async def delete_conversation(
    conversation_id: str,
    research_service: ResearchService = Depends(get_research_service),
):
    """
    Delete a research conversation.

    - **conversation_id**: ID of the conversation to delete
    """
    try:
        success = await research_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        return {
            "status": "success",
            "message": f"Conversation {conversation_id} deleted",
        }
    except Exception as e:
        # Log the exception here
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

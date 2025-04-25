"""
Pytest configuration for NYC Landmarks Research Agent.
Defines fixtures and configuration for tests.
"""
import os
import sys
import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.clients.vectorstore_client import VectorStoreClient
from src.clients.landmark_metadata_client import LandmarkMetadataClient
from src.clients.azure_openai_client import AzureOpenAIClient
from src.services.memory_service import MemoryService
from src.services.landmark_service import LandmarkService
from src.services.research_service import ResearchService


@pytest.fixture
def mock_vector_client():
    """Create a mock VectorStoreClient."""
    client = Mock(spec=VectorStoreClient)
    
    # Configure the mock to return sensible defaults
    client.query.return_value = {
        "results": [
            {
                "id": "test-chunk-1",
                "text": "This is a test passage about NYC landmarks.",
                "metadata": {
                    "title": "Test Document",
                    "landmark_id": "LP-00001",
                    "page": 1
                },
                "score": 0.95
            }
        ]
    }
    
    return client


@pytest.fixture
def mock_landmark_client():
    """Create a mock LandmarkMetadataClient."""
    client = Mock(spec=LandmarkMetadataClient)
    
    # Configure the mock to return a sample landmark
    client.get_landmark_by_id.return_value = {
        "lpc_id": "LP-00001",
        "name": "Test Landmark",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "borough": "Manhattan",
            "address": "123 Test Street"
        },
        "designation": {
            "designation_date": "2000-01-01T00:00:00",
            "designation_type": "Individual Landmark",
            "nycl_number": "LP-00001"
        }
    }
    
    client.search_landmarks.return_value = {
        "results": [
            {
                "lpc_id": "LP-00001",
                "name": "Test Landmark",
                "borough": "Manhattan",
                "designation_date": "2000-01-01T00:00:00"
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 10,
        "pages": 1
    }
    
    client.get_landmark_photos.return_value = [
        {
            "url": "https://example.com/photo1.jpg",
            "title": "Test Photo",
            "description": "A historic photo of Test Landmark",
            "year": 1950,
            "source": "NYC Archives",
            "is_historical": True
        }
    ]
    
    return client


@pytest.fixture
def mock_openai_client():
    """Create a mock AzureOpenAIClient."""
    client = AsyncMock(spec=AzureOpenAIClient)
    
    # Configure the mock to return a sample research report
    client.generate_text.return_value = "This is a sample research report about NYC landmarks."
    client.generate_research_report.return_value = "This is a sample research report about NYC landmarks."
    
    return client


@pytest.fixture
def mock_memory_service():
    """Create a mock MemoryService."""
    service = AsyncMock(spec=MemoryService)
    
    # Configure the mock with sensible behavior
    service.create_conversation.return_value = "test-conversation-id"
    service.get_conversation_history.return_value = [
        {"query": "Tell me about Test Landmark", "response": "Test Landmark is a historic building..."}
    ]
    service.add_entry.return_value = True
    service.delete_conversation.return_value = True
    
    return service


@pytest.fixture
def mock_landmark_service():
    """Create a mock LandmarkService."""
    service = AsyncMock(spec=LandmarkService)
    
    # Configure the mock with sensible behavior
    service.get_landmark_details.return_value = {
        "lpc_id": "LP-00001",
        "name": "Test Landmark",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "borough": "Manhattan",
            "address": "123 Test Street"
        },
        "designation": {
            "designation_date": "2000-01-01T00:00:00",
            "designation_type": "Individual Landmark",
            "nycl_number": "LP-00001"
        }
    }
    
    return service


@pytest.fixture
def mock_research_service(
    mock_vector_client, mock_landmark_client, mock_memory_service, mock_openai_client
):
    """Create a mock ResearchService."""
    return ResearchService(
        vector_client=mock_vector_client,
        landmark_client=mock_landmark_client,
        memory_service=mock_memory_service,
        openai_client=mock_openai_client
    )


@pytest.fixture
def sample_research_request() -> Dict[str, Any]:
    """Create a sample research request."""
    return {
        "query": "Tell me about the Flatiron Building",
        "conversation_id": None,
        "landmark_id": "LP-00004",
        "include_images": True,
        "max_sources": 5
    }


@pytest.fixture
def sample_conversation_id() -> str:
    """Return a sample conversation ID."""
    return "test-conversation-id"

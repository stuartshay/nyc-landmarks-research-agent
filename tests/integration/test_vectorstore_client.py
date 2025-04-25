"""
Integration tests for the VectorStoreClient.
Tests the client's ability to connect to the CoreDataStore Vector API.
"""
import pytest
import os
from unittest import mock
import asyncio
import requests

from src.clients.vectorstore_client import VectorStoreClient


# Skip these tests in CI environments or when the API is not available
skip_if_no_api = pytest.mark.skipif(
    "VECTOR_DB_API_URL" not in os.environ,
    reason="VECTOR_DB_API_URL environment variable not set"
)


@skip_if_no_api
@mock.patch.dict(os.environ, {"VECTOR_DB_API_URL": "https://vector-db.coredatastore.com"})
def test_vector_client_initialization():
    """Test that the vector client initializes properly."""
    # Arrange & Act
    client = VectorStoreClient()
    
    # Assert
    assert client is not None
    assert client.api_url == "https://vector-db.coredatastore.com"
    assert "accept" in client.headers
    assert "Content-Type" in client.headers


@skip_if_no_api
@mock.patch.dict(os.environ, {"VECTOR_DB_API_URL": "https://vector-db.coredatastore.com"})
@pytest.mark.asyncio
async def test_query_with_mock():
    """Test vector query with a mocked response."""
    # Arrange
    client = VectorStoreClient()
    mock_response = {
        "results": [
            {
                "id": "test-vector-1",
                "text": "This is a test passage about the Flatiron Building.",
                "metadata": {
                    "landmark_id": "LP-00004",
                    "title": "Flatiron Building Designation Report",
                    "page": 1
                },
                "score": 0.95
            }
        ]
    }
    
    # Mock the requests.post method
    with mock.patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = mock.Mock()
        
        # Act
        result = await asyncio.to_thread(
            client.query,
            query_text="Flatiron Building history",
            top_k=3,
            landmark_id="LP-00004"
        )
        
        # Assert
        assert result == mock_response
        mock_post.assert_called_once()
        
        # Verify the payload contains the expected fields
        call_args = mock_post.call_args[1]
        payload = call_args['json']
        assert payload['query'] == "Flatiron Building history"
        assert payload['top_k'] == 3
        assert 'filters' in payload
        assert payload['filters']['landmark_id'] == "LP-00004"


@skip_if_no_api
@mock.patch.dict(os.environ, {"VECTOR_DB_API_URL": "https://vector-db.coredatastore.com"})
@pytest.mark.asyncio
async def test_query_exception_handling():
    """Test vector query exception handling."""
    # Arrange
    client = VectorStoreClient()
    
    # Mock the requests.post method to raise an exception
    with mock.patch('requests.post') as mock_post:
        mock_post.side_effect = requests.RequestException("API connection error")
        
        # Act & Assert
        with pytest.raises(requests.RequestException):
            await asyncio.to_thread(
                client.query,
                query_text="Flatiron Building history"
            )


@skip_if_no_api
@mock.patch.dict(os.environ, {"VECTOR_DB_API_URL": "https://vector-db.coredatastore.com"})
@pytest.mark.asyncio
async def test_get_landmark_chunks_with_mock():
    """Test getting landmark chunks with a mocked response."""
    # Arrange
    client = VectorStoreClient()
    mock_response = {
        "results": [
            {
                "id": "chunk-1",
                "text": "The Flatiron Building was completed in 1902.",
                "metadata": {
                    "landmark_id": "LP-00004",
                    "page": 1
                },
                "score": 1.0
            },
            {
                "id": "chunk-2",
                "text": "The Flatiron Building was designed by Daniel Burnham.",
                "metadata": {
                    "landmark_id": "LP-00004",
                    "page": 2
                },
                "score": 1.0
            }
        ]
    }
    
    # Mock the requests.post method
    with mock.patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = mock.Mock()
        
        # Act
        result = await asyncio.to_thread(
            client.get_landmark_chunks,
            landmark_id="LP-00004",
            top_k=5
        )
        
        # Assert
        assert result == mock_response.get("results", [])
        mock_post.assert_called_once()
        
        # Verify the payload contains the expected fields
        call_args = mock_post.call_args[1]
        payload = call_args['json']
        assert payload['query'] == "*"  # Wildcard query
        assert payload['top_k'] == 5
        assert 'filters' in payload
        assert payload['filters']['landmark_id'] == "LP-00004"


@skip_if_no_api
@mock.patch.dict(os.environ, {"VECTOR_DB_API_URL": "https://vector-db.coredatastore.com"})
@pytest.mark.asyncio
async def test_get_document_with_mock():
    """Test getting a document by ID with a mocked response."""
    # Arrange
    client = VectorStoreClient()
    document_id = "test-document-1"
    mock_response = {
        "id": document_id,
        "text": "The Flatiron Building was completed in 1902.",
        "metadata": {
            "landmark_id": "LP-00004",
            "title": "Flatiron Building Designation Report",
            "page": 1
        }
    }
    
    # Mock the requests.get method
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = mock.Mock()
        
        # Act
        result = await asyncio.to_thread(
            client.get_document,
            document_id=document_id
        )
        
        # Assert
        assert result == mock_response
        mock_get.assert_called_once()
        
        # Verify the URL contains the document ID
        call_args = mock_get.call_args[0]
        url = call_args[0]
        assert document_id in url

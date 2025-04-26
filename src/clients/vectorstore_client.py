"""
Client for interacting with the CoreDataStore Vector DB API.
Provides semantic search capabilities over landmark text data.
"""

import json
import logging
from typing import Any, Dict, List, Optional

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.config import settings

logger = logging.getLogger(__name__)


class VectorStoreClient:
    """Client for interacting with the CoreDataStore Vector DB API."""

    def __init__(self, api_url: Optional[str] = None):
        """
        Initialize the vector store client.

        Args:
            api_url: URL for the Vector DB API. If not provided, uses the URL from settings.
        """
        self.api_url = api_url or str(settings.VECTOR_DB_API_URL)
        self.api_url = self.api_url.rstrip("/")
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError)),
        reraise=True,
    )
    def query(
        self,
        query_text: str,
        top_k: int = 5,
        landmark_id: Optional[str] = None,
        min_score: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Perform a semantic search query against the vector database.

        Args:
            query_text: The text query to search for
            top_k: Maximum number of results to return
            landmark_id: Optional landmark ID to filter results
            min_score: Minimum relevance score for results (0.0-1.0)

        Returns:
            Dictionary with query results

        Raises:
            requests.RequestException: If there's an API communication error
            ValueError: For invalid parameters or response format
        """
        endpoint = f"{self.api_url}/query"

        # Build payload
        payload = {"query": query_text, "top_k": top_k}

        # Add filters if provided
        filters = {}
        if landmark_id:
            filters["landmark_id"] = landmark_id

        if filters:
            payload["filters"] = filters

        if min_score > 0:
            payload["min_score"] = min_score

        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
        except requests.RequestException as e:
            logger.error(f"Vector search API request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in vector search: {str(e)}")
            raise ValueError(f"Error processing vector search results: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError)),
        reraise=True,
    )
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get a specific document from the vector database by ID.

        Args:
            document_id: ID of the document to retrieve

        Returns:
            Document data as a dictionary

        Raises:
            requests.RequestException: If there's an API communication error
            ValueError: For invalid parameters or response format
        """
        endpoint = f"{self.api_url}/document/{document_id}"

        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
        except requests.RequestException as e:
            logger.error(f"API request failed for document ID {document_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching document {document_id}: {str(e)}")
            raise ValueError(f"Error retrieving document: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError)),
        reraise=True,
    )
    def get_landmark_chunks(self, landmark_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get all text chunks for a specific landmark.

        Args:
            landmark_id: Landmark ID (e.g., "LP-00001")
            top_k: Maximum number of chunks to return

        Returns:
            List of text chunks

        Raises:
            requests.RequestException: If there's an API communication error
            ValueError: For invalid parameters or response format
        """
        # Use the query endpoint with a wildcard query but filtered to specific landmark
        endpoint = f"{self.api_url}/query"

        payload = {
            "query": "*",  # Wildcard query to match all documents
            "top_k": top_k,
            "filters": {"landmark_id": landmark_id},
        }

        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            results: List[Dict[str, Any]] = data.get("results", [])
            return results
        except requests.RequestException as e:
            logger.error(f"API request failed for landmark chunks {landmark_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching landmark chunks {landmark_id}: {str(e)}")
            raise ValueError(f"Error retrieving landmark chunks: {str(e)}")


if __name__ == "__main__":
    # Simple manual test
    client = VectorStoreClient()
    query = "Flatiron Building history"
    result = client.query(query)
    print(json.dumps(result, indent=2))

"""
Client for interacting with the CoreDataStore Landmark Metadata API.
Provides methods to fetch metadata about NYC landmarks.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from pydantic import ValidationError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.config import settings
from src.models.landmark_models import DesignationInfo, LandmarkDetail, LandmarkLocation, LandmarkSummary

logger = logging.getLogger(__name__)


class LandmarkMetadataClient:
    """Client for interacting with the CoreDataStore Landmark Metadata API."""

    def __init__(self, api_url: Optional[str] = None):
        """
        Initialize the landmark metadata client.

        Args:
            api_url: URL for the CoreDataStore Landmark Metadata API. If not provided,
                    uses the URL from settings.
        """
        self.api_url = api_url or str(settings.LANDMARK_METADATA_API_URL)
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
    def get_landmark_by_id(self, lpc_id: str) -> Optional[LandmarkDetail]:
        """
        Get detailed information about a specific landmark by LPC ID.

        Args:
            lpc_id: The Landmarks Preservation Commission ID (e.g., "LP-00001")

        Returns:
            LandmarkDetail object if found, None otherwise

        Raises:
            requests.RequestException: If there's an API communication error
            ValueError: For invalid parameters or response format
        """
        endpoint = f"{self.api_url}/api/LPCReport/{lpc_id}"

        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            if not data:
                logger.warning(f"No data found for landmark ID: {lpc_id}")
                return None

            return self._convert_to_landmark_detail(data)
        except requests.RequestException as e:
            logger.error(f"API request failed for landmark ID {lpc_id}: {str(e)}")
            raise
        except ValidationError as e:
            logger.error(f"Failed to parse landmark data for {lpc_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching landmark {lpc_id}: {str(e)}")
            raise ValueError(f"Error processing landmark data: {str(e)}")

    def _prepare_search_params(
        self,
        query: Optional[str] = None,
        borough: Optional[str] = None,
        neighborhood: Optional[str] = None,
        style: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """
        Prepare parameters for landmark search API request.

        Args:
            query: Text search query
            borough: Filter by borough name
            neighborhood: Filter by neighborhood
            style: Filter by architectural style
            page: Page number (1-based)
            page_size: Number of results per page

        Returns:
            Dictionary of query parameters for the API request
        """
        params: Dict[str, Any] = {"page": str(page), "limit": str(page_size)}

        # Add optional filters
        if query:
            params["SearchText"] = str(query)
        if borough:
            params["Borough"] = str(borough)
        if neighborhood:
            params["Neighborhood"] = str(neighborhood)
        if style:
            params["ParentStyleList"] = str(style)  # API handles comma-separated values

        return params

    def _process_search_results(self, data: Dict[str, Any], page: int, page_size: int) -> Dict[str, Any]:
        """
        Process landmark search API results.

        Args:
            data: Raw API response data
            page: Current page number
            page_size: Number of results per page

        Returns:
            Processed results with pagination info
        """
        results = []

        # Process each landmark in the results
        for item in data.get("results", []):
            try:
                landmark = self._convert_to_landmark_summary(item)
                results.append(landmark)
            except ValidationError as e:
                logger.warning(f"Failed to parse landmark data: {str(e)}")
                continue

        return {
            "results": results,
            "total": data.get("total", 0),
            "page": page,
            "page_size": page_size,
            "pages": (data.get("total", 0) + page_size - 1) // page_size,
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError)),
        reraise=True,
    )
    def search_landmarks(
        self,
        query: Optional[str] = None,
        borough: Optional[str] = None,
        neighborhood: Optional[str] = None,
        style: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """
        Search for landmarks with optional filters.

        Args:
            query: Text search query
            borough: Filter by borough name
            neighborhood: Filter by neighborhood
            style: Filter by architectural style
            page: Page number (1-based)
            page_size: Number of results per page

        Returns:
            Dictionary with results and pagination info

        Raises:
            requests.RequestException: If there's an API communication error
            ValueError: For invalid parameters or response format
        """
        endpoint = f"{self.api_url}/api/LPCReports"
        params = self._prepare_search_params(query, borough, neighborhood, style, page, page_size)

        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return self._process_search_results(data, page, page_size)
        except requests.RequestException as e:
            logger.error(f"API request failed for landmark search: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in landmark search: {str(e)}")
            raise ValueError(f"Error processing search results: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError)),
        reraise=True,
    )
    def get_landmark_photos(self, lpc_id: str) -> List[Dict[str, Any]]:
        """
        Get photos for a specific landmark.

        Args:
            lpc_id: The Landmarks Preservation Commission ID (e.g., "LP-00001")

        Returns:
            List of photo information dictionaries

        Raises:
            requests.RequestException: If there's an API communication error
            ValueError: For invalid parameters or response format
        """
        endpoint = f"{self.api_url}/api/LpcPhotoArchive"

        params: Dict[str, str] = {"LpcId": str(lpc_id), "limit": "50", "page": "1"}

        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            result_list: List[Dict[str, Any]] = data.get("results", [])
            return result_list
        except requests.RequestException as e:
            logger.error(f"API request failed for landmark photos {lpc_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching landmark photos {lpc_id}: {str(e)}")
            raise ValueError(f"Error processing photo data: {str(e)}")

    def _convert_to_landmark_detail(self, data: Dict[str, Any]) -> LandmarkDetail:
        """
        Convert API response to LandmarkDetail model.

        Args:
            data: API response data

        Returns:
            LandmarkDetail object
        """
        # Implementation would extract and transform fields from the API response
        # to match the LandmarkDetail schema. This is a placeholder that would
        # need to be completed with the actual field mappings.

        # For now, returning a minimal example
        try:
            # Extract basic information
            lpc_id = data.get("objectId") or data.get("lpcNumber") or ""
            name = data.get("name", "")
            borough = data.get("borough", "")

            # Create a basic LandmarkDetail object
            # In a real implementation, this would be more complete
            return LandmarkDetail(
                lpc_id=lpc_id,
                name=name,
                location=LandmarkLocation(
                    latitude=0.0,
                    longitude=0.0,
                    borough=borough,
                    address="",
                    neighborhood=None,
                    zipcode=None,
                ),
                designation=DesignationInfo(
                    designation_date=datetime.fromisoformat("2000-01-01T00:00:00"),
                    designation_type="Individual Landmark",
                    nycl_number=lpc_id,
                    designation_report_url=None,
                    significance_statement=None,
                ),
                alternate_names=[],
                description=None,
                style=None,
                building_type=None,
                architect=None,
                year_built=None,
                year_completed=None,
                pluto_data=None,
                historic_district=None,
                is_historic_district=False,
                related_landmarks=[],
                metadata={},
            )
        except Exception as e:
            logger.error(f"Error converting landmark data: {str(e)}, data: {json.dumps(data)[:200]}")
            raise

    def _convert_to_landmark_summary(self, data: Dict[str, Any]) -> LandmarkSummary:
        """
        Convert API response to LandmarkSummary model.

        Args:
            data: API response data

        Returns:
            LandmarkSummary object
        """
        # Implementation would extract and transform fields from the API response
        # to match the LandmarkSummary schema. This is a placeholder.

        # For now, returning a minimal example
        lpc_id = data.get("objectId") or data.get("lpcNumber") or ""
        name = data.get("name", "")
        borough = data.get("borough", "")

        # Create a basic LandmarkSummary object
        return LandmarkSummary(
            lpc_id=lpc_id,
            name=name,
            borough=borough,
            designation_date=datetime.fromisoformat("2000-01-01T00:00:00"),
            style=None,
            year_built=None,
            primary_photo_url=None,
        )

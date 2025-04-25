"""
Landmark service for the NYC Landmarks Research Agent.
Provides methods for retrieving and processing landmark information.
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
import asyncio

from src.clients.landmark_metadata_client import LandmarkMetadataClient
from src.models.landmark_models import LandmarkDetail, LandmarkSummary, LandmarkPhoto

logger = logging.getLogger(__name__)


class LandmarkService:
    """Service for retrieving and processing landmark information."""
    
    def __init__(self, landmark_client: Optional[LandmarkMetadataClient] = None):
        """
        Initialize the landmark service.
        
        Args:
            landmark_client: Optional LandmarkMetadataClient instance to use.
                            If not provided, a new client will be created.
        """
        self.landmark_client = landmark_client or LandmarkMetadataClient()
        logger.info("Landmark service initialized")
    
    async def get_landmark_details(self, landmark_id: str) -> Optional[LandmarkDetail]:
        """
        Get detailed information about a landmark by its ID.
        
        Args:
            landmark_id: The Landmarks Preservation Commission ID (e.g., "LP-00001")
            
        Returns:
            LandmarkDetail object if found, None otherwise
        """
        try:
            logger.debug(f"Fetching details for landmark {landmark_id}")
            landmark = await asyncio.to_thread(
                self.landmark_client.get_landmark_by_id,
                landmark_id
            )
            return landmark
        except Exception as e:
            logger.error(f"Error fetching landmark details for {landmark_id}: {str(e)}")
            return None
    
    async def search_landmarks(
        self,
        query: Optional[str] = None,
        borough: Optional[str] = None,
        neighborhood: Optional[str] = None,
        style: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
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
            Dictionary with search results and pagination information
        """
        try:
            filters = []
            if query:
                filters.append(f"query='{query}'")
            if borough:
                filters.append(f"borough='{borough}'")
            if neighborhood:
                filters.append(f"neighborhood='{neighborhood}'")
            if style:
                filters.append(f"style='{style}'")
                
            filter_str = " and ".join(filters) if filters else "no filters"
            logger.debug(f"Searching landmarks with {filter_str}, page={page}, page_size={page_size}")
            
            results = await asyncio.to_thread(
                self.landmark_client.search_landmarks,
                query=query,
                borough=borough,
                neighborhood=neighborhood,
                style=style,
                page=page,
                page_size=page_size
            )
            
            landmark_count = len(results.get("results", []))
            logger.debug(f"Found {landmark_count} landmarks, total={results.get('total', 0)}")
            return results
        except Exception as e:
            logger.error(f"Error searching landmarks: {str(e)}")
            return {"results": [], "total": 0, "page": page, "page_size": page_size, "pages": 0}
    
    async def get_landmark_photos(self, landmark_id: str) -> List[LandmarkPhoto]:
        """
        Get photos for a landmark.
        
        Args:
            landmark_id: The Landmarks Preservation Commission ID (e.g., "LP-00001")
            
        Returns:
            List of LandmarkPhoto objects
        """
        try:
            logger.debug(f"Fetching photos for landmark {landmark_id}")
            photos_data = await asyncio.to_thread(
                self.landmark_client.get_landmark_photos,
                landmark_id
            )
            
            photos = []
            for photo_data in photos_data:
                try:
                    # Convert each photo data to a LandmarkPhoto object
                    # This is a simplified example - in a real implementation
                    # you would map the actual fields from the API response
                    photo = LandmarkPhoto(
                        url=photo_data.get("url", ""),
                        title=photo_data.get("title"),
                        description=photo_data.get("description"),
                        year=photo_data.get("year"),
                        source=photo_data.get("source"),
                        is_historical=photo_data.get("is_historical", False)
                    )
                    photos.append(photo)
                except Exception as e:
                    logger.warning(f"Error converting photo data: {str(e)}")
                    continue
                    
            logger.debug(f"Found {len(photos)} photos for landmark {landmark_id}")
            return photos
        except Exception as e:
            logger.error(f"Error fetching landmark photos for {landmark_id}: {str(e)}")
            return []
    
    async def find_landmark_by_name(
        self, 
        name: str,
        exact_match: bool = False
    ) -> Tuple[Optional[str], Optional[LandmarkSummary]]:
        """
        Find a landmark by name.
        
        Args:
            name: Name of the landmark to find
            exact_match: Whether to require an exact match
            
        Returns:
            Tuple of (landmark_id, landmark_summary) if found, (None, None) otherwise
        """
        try:
            logger.debug(f"Finding landmark by name: {name}")
            results = await self.search_landmarks(query=name, page_size=5)
            
            landmarks = results.get("results", [])
            if not landmarks:
                logger.debug(f"No landmarks found matching name: {name}")
                return None, None
                
            # If exact match is required, check for an exact match
            if exact_match:
                for landmark in landmarks:
                    if landmark.name.lower() == name.lower():
                        logger.debug(f"Found exact match for {name}: {landmark.lpc_id}")
                        return landmark.lpc_id, landmark
                
                logger.debug(f"No exact match found for {name}")
                return None, None
                
            # Otherwise, return the first match
            landmark = landmarks[0]
            logger.debug(f"Found best match for {name}: {landmark.lpc_id} ({landmark.name})")
            return landmark.lpc_id, landmark
        except Exception as e:
            logger.error(f"Error finding landmark by name {name}: {str(e)}")
            return None, None

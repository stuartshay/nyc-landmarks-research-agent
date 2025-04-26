"""
Landmark data models for the NYC Landmarks Research Agent.
Defines data structures for landmarks and related entities.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class LandmarkLocation(BaseModel):
    """Geographic location and address information of a landmark."""

    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    borough: str = Field(
        ...,
        description="NYC borough (Manhattan, Brooklyn, Queens, Bronx, Staten Island)",
    )
    neighborhood: Optional[str] = Field(None, description="Neighborhood name")
    address: str = Field(..., description="Street address")
    zipcode: Optional[str] = Field(None, description="Postal code")


class LandmarkPhoto(BaseModel):
    """Photo of a landmark with metadata."""

    url: HttpUrl = Field(..., description="URL to the image")
    title: Optional[str] = Field(None, description="Title of the photo")
    description: Optional[str] = Field(None, description="Description of the image")
    year: Optional[int] = Field(None, description="Year the photo was taken")
    photographer: Optional[str] = Field(None, description="Name of photographer")
    source: Optional[str] = Field(None, description="Source of the photo")
    is_historical: bool = Field(False, description="Whether this is a historical photo")
    is_primary: bool = Field(False, description="Whether this is the primary photo")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")


class Architect(BaseModel):
    """Information about an architect or architectural firm."""

    name: str = Field(..., description="Name of the architect or firm")
    info: Optional[str] = Field(None, description="Brief information about the architect")
    period: Optional[str] = Field(None, description="Active period of the architect")
    other_works: Optional[List[str]] = Field(None, description="Other notable works by the architect")


class DesignationInfo(BaseModel):
    """Information about landmark designation."""

    designation_date: datetime = Field(..., description="Date of landmark designation")
    designation_type: str = Field(
        ...,
        description="Type of designation (e.g., 'Individual Landmark', 'Historic District')",
    )
    designation_report_url: Optional[HttpUrl] = Field(None, description="URL to the designation report")
    nycl_number: str = Field(..., description="NYC Landmarks Commission number (e.g., 'LP-00001')")
    significance_statement: Optional[str] = Field(None, description="Statement of significance")


class PlutoData(BaseModel):
    """PLUTO database information for the landmark."""

    block: Optional[int] = Field(None, description="Tax block number")
    lot: Optional[int] = Field(None, description="Tax lot number")
    bbl: Optional[str] = Field(None, description="Borough-Block-Lot identifier")
    zoning: Optional[str] = Field(None, description="Zoning designation")
    year_built: Optional[int] = Field(None, description="Year of construction")
    num_floors: Optional[float] = Field(None, description="Number of floors")
    building_class: Optional[str] = Field(None, description="Building class code")
    far: Optional[float] = Field(None, description="Floor area ratio")
    lot_area: Optional[float] = Field(None, description="Lot area in square feet")
    building_area: Optional[float] = Field(None, description="Building area in square feet")


class LandmarkDetail(BaseModel):
    """Detailed information about a landmark."""

    lpc_id: str = Field(..., description="Landmarks Preservation Commission ID")
    name: str = Field(..., description="Name of the landmark")
    alternate_names: Optional[List[str]] = Field([], description="Alternative names")
    description: Optional[str] = Field(None, description="Brief description")
    style: Optional[str] = Field(None, description="Architectural style")
    building_type: Optional[str] = Field(None, description="Type of building or structure")
    architect: Optional[Architect] = Field(None, description="Architect information")
    year_built: Optional[int] = Field(None, description="Year of construction")
    year_completed: Optional[int] = Field(None, description="Year of completion if different from built")
    location: LandmarkLocation = Field(..., description="Location information")
    designation: DesignationInfo = Field(..., description="Designation information")
    photos: List[LandmarkPhoto] = Field(default_factory=list, description="Photos of the landmark")
    pluto_data: Optional[PlutoData] = Field(None, description="PLUTO database information")
    historic_district: Optional[str] = Field(None, description="Historic district name if applicable")
    is_historic_district: bool = Field(False, description="Whether this is a historic district")
    related_landmarks: Optional[List[Dict[str, str]]] = Field([], description="Related landmarks")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")


class LandmarkSummary(BaseModel):
    """Summary information about a landmark, used for listings and search results."""

    lpc_id: str = Field(..., description="Landmarks Preservation Commission ID")
    name: str = Field(..., description="Name of the landmark")
    style: Optional[str] = Field(None, description="Architectural style")
    year_built: Optional[int] = Field(None, description="Year of construction")
    borough: str = Field(..., description="NYC borough")
    designation_date: datetime = Field(..., description="Date of landmark designation")
    primary_photo_url: Optional[HttpUrl] = Field(None, description="URL to primary photo")

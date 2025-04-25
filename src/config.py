"""
Configuration settings for the NYC Landmarks Research Agent.
Uses Pydantic BaseSettings to load environment variables with dotenv support.
"""
import os
from pydantic_settings import BaseSettings
from pydantic import HttpUrl, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Clean environment variables that might have inline comments
if "ENABLE_MEMORY" in os.environ:
    value = os.environ["ENABLE_MEMORY"].split("#")[0].strip()
    os.environ["ENABLE_MEMORY"] = value

if "MEMORY_TTL_SECONDS" in os.environ:
    value = os.environ["MEMORY_TTL_SECONDS"].split("#")[0].strip()
    os.environ["MEMORY_TTL_SECONDS"] = value

if "LOG_LEVEL" in os.environ:
    value = os.environ["LOG_LEVEL"].split("#")[0].strip()
    os.environ["LOG_LEVEL"] = value


class Settings(BaseSettings):
    """Application settings, loaded from environment variables."""

    # API URLs
    VECTOR_DB_API_URL: HttpUrl = Field(
        ...,
        description="URL for the CoreDataStore Vector API"
    )
    LANDMARK_METADATA_API_URL: HttpUrl = Field(
        ...,
        description="URL for the CoreDataStore Landmark Metadata API"
    )

    # Azure OpenAI configuration
    OPENAI_API_KEY: str = Field(
        ...,
        description="API key for Azure OpenAI"
    )
    AZURE_OPENAI_ENDPOINT: HttpUrl = Field(
        ...,
        description="Endpoint URL for Azure OpenAI"
    )
    AZURE_OPENAI_DEPLOYMENT: str = Field(
        "gpt-4",
        description="Azure OpenAI deployment name/model to use"
    )

    # Application settings
    LOG_LEVEL: str = Field(
        "INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    ENABLE_MEMORY: bool = Field(
        True,
        description="Enable conversation memory"
    )
    MEMORY_TTL_SECONDS: int = Field(
        86400,  # 24 hours
        description="Time-to-live for memory entries in seconds"
    )
    APP_NAME: str = Field(
        "NYC Landmarks Research Agent",
        description="Name of the application"
    )
    APP_VERSION: str = Field(
        "0.1.0",
        description="Application version"
    )

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create a global instance of settings
settings = Settings()

# Constants for application
VECTOR_DB_API_URL = settings.VECTOR_DB_API_URL
LANDMARK_METADATA_API_URL = settings.LANDMARK_METADATA_API_URL
OPENAI_API_KEY = settings.OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT = settings.AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT = settings.AZURE_OPENAI_DEPLOYMENT

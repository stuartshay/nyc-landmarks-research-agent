# NYC Landmarks Research Agent - Technical Context

## Technology Stack

### Backend Framework
- **Python 3.9+**: Core programming language
- **FastAPI**: High-performance web framework for building APIs
- **Uvicorn**: ASGI server for running the FastAPI application
- **Pydantic**: Data validation and settings management

### External APIs
- **CoreDataStore Vector API**: Semantic search over landmark documents
- **CoreDataStore Landmark API**: Structured metadata about landmarks
- **Azure OpenAI Service**: AI model for generating research reports

### Data Management
- **In-memory storage**: For development conversation memory
- **Redis**: Planned for production conversation memory storage
- **PostgreSQL**: Used by CoreDataStore for structured data (indirect dependency)

### Development Tools
- **Docker**: Containerization for development and deployment
- **docker-compose**: Multi-container Docker applications
- **pre-commit**: Git hooks for code quality
- **flake8**: Python code linting
- **pytest**: Testing framework
- **tenacity**: Retry logic for API calls

### Deployment
- **Google Cloud Run**: Planned containerized deployment platform
- **GitHub Actions**: CI/CD pipeline

## Development Environment

### Local Setup
1. Python 3.9+ environment
2. .env file with required API keys and endpoints:
   - VECTOR_DB_API_URL
   - LANDMARK_METADATA_API_URL
   - OPENAI_API_KEY
   - AZURE_OPENAI_ENDPOINT
   - AZURE_OPENAI_DEPLOYMENT
3. Docker and docker-compose for containerized development

### Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.main
```

### Docker Setup
```bash
# Build and run with docker-compose
docker-compose up --build
```

## Technical Constraints

### API Dependencies
- Requires access to CoreDataStore Vector API for semantic search
- Requires access to CoreDataStore Landmark API for metadata
- Requires Azure OpenAI API key and endpoint

### Performance Considerations
- API response times dependent on external service latency
- Azure OpenAI token limits constrain research report length
- Memory storage TTL settings impact conversation context retention

### Security Requirements
- API keys must be securely stored and transmitted
- CORS configuration for production deployment
- Input validation to prevent injection attacks

### Scalability Considerations
- In-memory storage is not suitable for production-scale deployment
- Redis recommended for production conversation memory
- Azure OpenAI service quotas may limit concurrent requests

## External Integrations

### CoreDataStore Vector API
- Provides semantic search over landmark documents
- Returns relevant passages with metadata
- Supports filtering by landmark ID and other attributes

```json
// Example Vector Search Response
{
  "results": [
    {
      "id": "chunk123",
      "text": "The Flatiron Building was completed in 1902...",
      "metadata": {
        "title": "Flatiron Building Designation Report",
        "page": 4,
        "landmark_id": "LP-00073"
      },
      "score": 0.89
    }
  ],
  "total": 1
}
```

### CoreDataStore Landmark API
- Provides structured metadata about landmarks
- Includes designation information, location data, and architectural details
- Supports search and filtering capabilities

```json
// Example Landmark Response
{
  "objectId": "LP-00073",
  "name": "Flatiron Building",
  "borough": "Manhattan",
  "designation_date": "1966-09-20T00:00:00",
  "style": "Beaux-Arts"
}
```

### Azure OpenAI Service
- Provides AI model for generating research reports
- Uses system prompts to guide report structure and content
- Requires careful prompt engineering for optimal results

## Data Models

### Key Entities
- **Landmark**: A designated NYC landmark with metadata
- **Research Report**: Generated content about landmarks
- **Conversation**: A series of research queries and responses
- **Source Document**: A reference document with landmark information
- **Image**: A photo of a landmark with metadata

### Entity Relationships
- Landmarks have many Source Documents (1:N)
- Landmarks have many Images (1:N)
- Research Reports reference many Source Documents (N:M)
- Conversations contain many Research Reports (1:N)
- Research Reports may reference many Landmarks (N:M)

## Deployment Strategy

### Development
- Local development with direct API connections
- Docker containers for consistent environment
- Mocked external services for testing

### Staging
- Google Cloud Run deployment
- Integration with actual external APIs
- Performance testing and optimization

### Production
- Google Cloud Run with auto-scaling
- Redis for conversation memory
- Monitoring and logging setup
- Rate limiting for API endpoints

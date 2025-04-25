# NYC Landmarks Research Agent - Project Brief

## Project Overview
The NYC Landmarks Research Agent is an AI-powered system designed to generate in-depth, accurate, and engaging research reports about New York City landmarks. The agent combines semantic search over landmark PDF reports with structured metadata retrieval to provide comprehensive information about NYC's architectural and cultural heritage.

## Core Requirements
1. Connect to CoreDataStore Vector API for semantic search over landmark reports
2. Connect to CoreDataStore Landmark API for structured metadata
3. Implement conversation memory for contextual follow-up questions
4. Generate research reports using Azure OpenAI Service
5. Support filtering by landmark ID, borough, and other metadata
6. Include modern and historical photos in research reports
7. Create RESTful API for client applications
8. Implement dockerized deployment for cloud services

## Key Goals
- Create an intelligent agent that can answer detailed questions about NYC landmarks
- Combine structured metadata with unstructured knowledge from reports
- Enable conversational research with memory of previous interactions
- Deliver research reports in a well-structured, educational format
- Support both broad queries and specific landmark focus
- Include visual elements (photos) in research results
- Create a scalable, maintainable architecture for the system
- Implement secure credential management

## Success Criteria
- Agent generates accurate, well-structured research reports based on user queries
- Semantic search returns relevant passages from landmark documents
- Reports include appropriate citations and references
- Conversation memory enables contextual follow-up questions
- Images are included when available and relevant
- API performance is optimized for reasonable response times
- System can be deployed as a containerized service
- Secure handling of credentials and API keys

## Technical Approach
- **Language**: Python 3.9+ with FastAPI
- **Vector Search**: CoreDataStore Vector API
- **Metadata**: CoreDataStore Landmark API
- **AI Model**: Azure OpenAI Service (GPT-4 preferred)
- **Memory**: In-memory storage with TTL for development, Redis for production
- **Deployment**: Docker containers with Google Cloud Run
- **CI/CD**: GitHub Actions for testing and deployment
- **Security**: Secret management with environment variables and cloud secret stores

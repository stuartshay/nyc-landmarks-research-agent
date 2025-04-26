# Copilot Instructions for NYC Landmarks Research Agent

## Project Overview
The NYC Landmarks Research Agent is an AI-powered system that generates detailed, accurate, and engaging research reports about New York City landmarks. It combines semantic search over landmark PDF reports with structured metadata retrieval to provide comprehensive information about NYC's architectural and cultural heritage.

## Core Requirements
- Integrate with CoreDataStore Vector API for semantic search over landmark reports.
- Integrate with CoreDataStore Landmark API for structured metadata.
- Implement conversation memory for contextual follow-up questions.
- Generate research reports using Azure OpenAI Service.
- Support filtering by landmark ID, borough, and other metadata.
- Include modern and historical photos in research reports.
- Provide a RESTful API for client applications.
- Support dockerized deployment for cloud services.

## Key Goals
- Deliver intelligent, conversational research about NYC landmarks.
- Combine structured metadata with unstructured knowledge from reports.
- Enable contextual follow-up questions using conversation memory.
- Generate well-structured, educational research reports with citations.
- Include relevant images in research results.
- Ensure scalable, maintainable, and secure architecture.

## Success Criteria
- Accurate, well-structured research reports based on user queries.
- Relevant semantic search results with proper citations.
- Effective conversation memory for contextual queries.
- Inclusion of images when available and relevant.
- Optimized API performance and containerized deployment.
- Secure handling of credentials and API keys.

## Technical Approach
- **Language:** Python 3.9+ with FastAPI
- **Vector Search:** CoreDataStore Vector API
- **Metadata:** CoreDataStore Landmark API
- **AI Model:** Azure OpenAI Service (GPT-4 preferred)
- **Memory:** In-memory storage (dev), Redis (prod)
- **Deployment:** Docker containers, Google Cloud Run
- **CI/CD:** GitHub Actions
- **Security:** Environment variables and cloud secret stores

## Best Practices
- **Code Quality:**
  - Follow PEP8 and use type annotations.
  - Write modular, testable code with clear docstrings.
  - Use pre-commit hooks (black, isort, flake8, mypy, bandit) to enforce standards.
- **Security:**
  - Never hardcode credentials or API keys; use environment variables or secret stores.
  - Always set timeouts for external API requests.
  - Use Bandit to check for common security issues.
- **Collaboration:**
  - Use clear, descriptive commit messages.
  - Document new features and changes in the README or relevant docs.
  - Write and maintain unit and integration tests for new code.
- **API Design:**
  - Follow RESTful conventions for endpoints.
  - Validate and sanitize all user inputs.
  - Provide clear error messages and status codes.
- **Deployment:**
  - Use Docker for local development and production deployment.
  - Store secrets securely and never commit them to version control.
- **Completion Rule:**
  - Before marking any task or pull request as complete, you **must** run `pre-commit run --all-files` and resolve all issues. Code should not be considered ready for review or merge until all pre-commit hooks pass successfully.

---

For more details, see `memory-bank/projectbrief.md` and the project README.

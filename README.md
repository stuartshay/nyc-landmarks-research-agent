# NYC Landmarks Research Agent

An AI-powered agent to generate research reports about NYC landmarks, leveraging vector search and structured metadata.

## Overview

The NYC Landmarks Research Agent combines semantic search over landmark designation reports with structured metadata retrieval to provide comprehensive and accurate information about New York City's architectural and cultural landmarks.

## Features

- Semantic search over landmark PDF documents
- Structured metadata retrieval from CoreDataStore
- AI-generated research reports using Azure OpenAI
- Conversation memory for contextual follow-up questions
- Support for filtering by landmark ID, borough, and other metadata
- Modern and historical landmark photos
- RESTful API interface

## Installation

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nyc-landmarks-research-agent.git
   cd nyc-landmarks-research-agent
   ```

2. Set up a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Create a `.env` file based on `.env.sample` with your API keys and configuration.

### Using Docker

```bash
docker-compose up
```

## Usage

### Running the API Server

```bash
uvicorn src.main:app --reload
```

The API will be available at http://localhost:8000

### API Documentation

Once the server is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

## Testing

### Running Tests in VS Code

Tests are set up to appear in the VS Code Test Explorer. To run tests:

1. Open the Testing panel in VS Code (test tube icon in the sidebar)
2. Click the "Run All Tests" button or run specific test files/suites

### Running Tests from the Command Line

Run all tests:
```bash
pytest
```

Run unit tests only:
```bash
pytest tests/unit
```

Run integration tests only:
```bash
pytest tests/integration
```

Run with coverage report:
```bash
pytest --cov=src --cov-report=term-missing
```

### Debugging Tests

VS Code launch configurations are provided for debugging:

1. Open the Run and Debug panel in VS Code
2. Select one of the test configurations:
   - "Python: All Tests"
   - "Python: Unit Tests"
   - "Python: Integration Tests"
3. Start debugging (F5)

## Project Structure

```
.
├── src/                      # Source code
│   ├── api/                  # API routes
│   ├── clients/              # External API clients
│   ├── endpoints/            # API endpoint implementations
│   ├── models/               # Data models
│   ├── services/             # Business logic services
│   └── util/                 # Utility functions
│
├── tests/                    # Test suite
│   ├── integration/          # Integration tests
│   └── unit/                 # Unit tests
│
├── .env.sample               # Sample environment variables
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
├── pyproject.toml            # Python project configuration
└── setup.py                  # Package setup script
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

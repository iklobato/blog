# Blog API

This project is a simple blog API built using FastAPI, PostgreSQL, and Redis. It allows users to create blog posts, add comments, and retrieve posts with comments. The application is containerized using Docker and managed with Docker Compose.

## Features
- Create, read, and manage blog posts
- Add comments to posts
- Cache posts and comments using Redis
- Use PostgreSQL for persistent data storage
- Comprehensive test suite with pytest
- Production-ready Docker configuration

## Prerequisites
- Docker
- Docker Compose

## Setup and Running

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd prosigliere-code
   ```

2. **Build and start the services**
   ```bash
   docker compose up --build -d
   ```
   This command will build the Docker images and start the services defined in the `compose.yaml` file.

3. **Access the API**
   - The API will be available at `http://localhost:8000`
   - API documentation is available at `http://localhost:8000/docs`
   - Health check endpoint: `http://localhost:8000/health`

## API Endpoints

- `GET /api/posts` - List all blog posts with comment counts
- `POST /api/posts` - Create a new blog post
- `GET /api/posts/{id}` - Get a specific post with all comments
- `POST /api/posts/{id}/comments` - Add a comment to a post
- `GET /health` - Health check endpoint

## Project Structure
- `app.py`: Main application file containing the FastAPI app and endpoints
- `Dockerfile`: Multi-stage Docker configuration for optimized production builds
- `compose.yaml`: Docker Compose configuration for PostgreSQL, Redis, and API services
- `requirements.txt`: Python dependencies with pinned versions
- `pyproject.toml`: Project configuration including test and linting settings
- `test/`: Test suite with comprehensive coverage
  - `conftest.py`: Test fixtures and mocks
  - `test_blog.py`: API endpoint tests
  - `test_crud.py`: Additional CRUD operation tests
  - `test_payloads.py`: Payload validation tests

## Dependencies

The application uses the following key dependencies:
- `fastapi==0.115.6` - Web framework
- `uvicorn[standard]==0.34.3` - ASGI server
- `asyncpg==0.30.0` - PostgreSQL async driver
- `redis==5.2.1` - Redis async client
- `pydantic==2.10.6` - Data validation

## Environment Variables
- `DATABASE_URL`: URL for connecting to the PostgreSQL database (default: `postgresql://postgres:password@localhost:5432/blog_db`)
- `REDIS_URL`: URL for connecting to the Redis server (default: `redis://localhost:6379`)

## Development

### Running Tests
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest test/test_blog.py
```

### Linting and Formatting
```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type checking
uv run mypy app.py
```

### Local Development (without Docker)
```bash
# Install dependencies
uv pip install -r requirements.txt

# Start PostgreSQL and Redis locally, then run:
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Docker Services

- **API**: FastAPI application running on port 8000
- **PostgreSQL**: Database server on port 5432
- **Redis**: Cache server on port 6379

## Notes
- Ensure Docker is running before starting the services
- The database and Redis data are persisted in Docker volumes
- The application includes automatic database table creation on startup
- Redis caching is used for improved performance with 5-minute TTL
- All tests run offline using mocked dependencies 
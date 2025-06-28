# Blog API

This project is a simple blog API built using FastAPI, PostgreSQL, and Redis. It allows users to create blog posts, add comments, and retrieve posts with comments. The application is containerized using Docker and managed with Docker Compose.

## Features
- Create, read, and manage blog posts
- Add comments to posts
- Cache posts and comments using Redis
- Use PostgreSQL for persistent data storage

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
   docker-compose up --build -d
   ```
   This command will build the Docker images and start the services defined in the `compose.yaml` file.

3. **Access the API**
   - The API will be available at `http://localhost:8000`
   - API documentation is available at `http://localhost:8000/docs`

## Project Structure
- `app.py`: Main application file containing the FastAPI app and endpoints.
- `Dockerfile`: Docker configuration for building the application image.
- `compose.yaml`: Docker Compose configuration for managing multi-container applications.
- `requirements.txt`: Python dependencies for the application.

## Environment Variables
- `DATABASE_URL`: URL for connecting to the PostgreSQL database.
- `REDIS_URL`: URL for connecting to the Redis server.

## Development

- **Run tests**
  ```bash
  uv run pytest
  ```

- **Linting and Formatting**
  ```bash
  uv run flake8
  uv run black .
  ```

## Notes
- Ensure Docker is running before starting the services.
- The database and Redis data are persisted in Docker volumes. 
# Items API with PostgreSQL/MySQL

FastAPI REST service for managing items with PostgreSQL or MySQL database support.

## Features

- **CRUD operations** for items (Create, Read, Update, Delete)
- **UUID-based identification** for each item
- **Multiple database support**: PostgreSQL or MySQL with SQLAlchemy async ORM
- **Redis caching** for improved read performance
- **Auto-generated API docs** at `/docs`
- **Health check endpoint** for monitoring
- **Docker support** for easy deployment
- **Async/await** for better performance

## Prerequisites

### Option 1: Docker (Recommended)
- Docker
- Docker Compose

### Option 2: Local Development
- Python 3.10+
- PostgreSQL 12+ OR MySQL 8.0+

## Setup

### Option A: Docker Setup (Recommended)

The easiest way to run the application is using Docker Compose:

**With PostgreSQL (default):**
```bash
# Build and start all services (API + PostgreSQL)
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

**With MySQL:**
```bash
# Build and start all services (API + MySQL)
docker-compose -f docker-compose.mysql.yml up --build

# Or run in detached mode
docker-compose -f docker-compose.mysql.yml up -d
```

**Stop services:**
```bash
docker-compose down              # PostgreSQL
# OR
docker-compose -f docker-compose.mysql.yml down   # MySQL

# Stop and remove volumes (clears database)
docker-compose down -v
```

The API will be available at `http://localhost:8000`

**Docker Services:**
- **API**: FastAPI application (port 8000)
- **Database**: PostgreSQL 15 (port 5432) OR MySQL 8.0 (port 3306)
- **Redis**: Cache server (port 6379)
- **Volumes**: Persistent storage for database and cache data

### Option B: Local Development Setup

### 1. Install Database

**Option 1: PostgreSQL**

```bash
# macOS (using Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create the database
createdb items_db
```

**Option 2: MySQL**

```bash
# macOS (using Homebrew)
brew install mysql
brew services start mysql

# Create the database and user
mysql -u root -e "CREATE DATABASE items_db;"
mysql -u root -e "CREATE USER 'items_user'@'localhost' IDENTIFIED BY 'items_pass';"
mysql -u root -e "GRANT ALL PRIVILEGES ON items_db.* TO 'items_user'@'localhost';"
mysql -u root -e "FLUSH PRIVILEGES;"
```

### 2. Install Redis

```bash
# macOS (using Homebrew)
brew install redis
brew services start redis

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### 3. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update the configuration:

```bash
cp .env.example .env
```

**Database URL - For PostgreSQL:**
```
DATABASE_URL=postgresql+asyncpg://domingossoares@localhost:5432/items_db
```
**Note**: On macOS with Homebrew PostgreSQL, use your system username (no password needed for local connections).

**Database URL - For MySQL:**
```
DATABASE_URL=mysql+aiomysql://items_user:items_pass@localhost:3306/items_db
```

**Redis Configuration:**
```
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300
```

### 5. Run the Server

```bash
./venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## Caching Behavior

The API uses Redis for caching to improve read performance:

- **Cached Endpoints**:
  - `GET /items` - All items list (cached for 5 minutes by default)
  - `GET /items/{uuid}` - Individual item (cached for 5 minutes by default)

- **Cache Invalidation**:
  - Cache is automatically invalidated on write operations:
    - `POST /items` - Clears all items list cache
    - `PUT /items/{uuid}` - Clears specific item and all items list cache
    - `DELETE /items/{uuid}` - Clears specific item and all items list cache

- **Cache TTL**: Configurable via `CACHE_TTL` environment variable (default: 300 seconds)

- **Graceful Degradation**: If Redis is unavailable, the API continues to work by querying the database directly

## API Endpoints

### GET `/items`
List all items (cached).

### GET `/items/{uuid}`
Get a specific item by UUID.

### POST `/items`
Create a new item (UUID auto-generated if not provided).

**Required fields:**
- `name` (string)
- `price` (number)

**Optional fields:**
- `id` (string, UUID format) - auto-generated if omitted
- `description` (string or null)
- `in_stock` (boolean) - defaults to `true`

**Request body example:**
```json
{
  "name": "Widget",
  "description": "A great widget",
  "price": 19.99,
  "in_stock": true
}
```

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Widget",
  "description": "A great widget",
  "price": 19.99,
  "in_stock": true
}
```

### PUT `/items/{uuid}`
Update an existing item.

### DELETE `/items/{uuid}`
Delete an item.

### GET `/health`
Health check endpoint - verifies API and database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "api": "healthy",
  "database": "healthy"
}
```

## Docker Commands (Makefile)

If using Docker, you can use these convenient commands:

```bash
make help     # Show all available commands
make build    # Build Docker images
make up       # Start all services in background
make down     # Stop all services
make logs     # View logs
make restart  # Restart services
make clean    # Remove all containers, volumes, and images
```

## Quick API Testing

Test the API using curl:

```bash
# Health check
curl http://localhost:8000/health

# List all items
curl http://localhost:8000/items

# Create an item
curl -X POST "http://localhost:8000/items" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item", "price": 29.99}'

# Get specific item (replace {uuid} with actual UUID)
curl http://localhost:8000/items/{uuid}

# Update item
curl -X PUT "http://localhost:8000/items/{uuid}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Item", "price": 39.99}'

# Delete item
curl -X DELETE "http://localhost:8000/items/{uuid}"
```

## Interactive API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```
project-7/
├── main.py                    # FastAPI application and routes
├── database.py                # Database connection and session management
├── models.py                  # SQLAlchemy ORM models (PostgreSQL/MySQL compatible)
├── cache.py                   # Redis caching utilities
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker image configuration
├── docker-compose.yml         # Docker services (PostgreSQL + Redis)
├── docker-compose.mysql.yml   # Docker services (MySQL + Redis)
├── Makefile                   # Convenient commands for Docker
├── .env.example              # Example environment variables
├── .dockerignore             # Files to exclude from Docker build
└── README.md                 # This file
```

## Database Schema

### Items Table

| Column      | Type    | Description              |
|-------------|---------|--------------------------|
| id          | UUID*   | Primary key (auto)       |
| name        | String  | Item name (required)     |
| description | Text    | Item description (optional) |
| price       | Float   | Item price (required)    |
| in_stock    | Boolean | Stock status (default: true) |

**Note**: UUID is stored natively in PostgreSQL and as CHAR(36) in MySQL, but the API handles UUIDs transparently regardless of the database backend.

# Items API with PostgreSQL

FastAPI REST service for managing items with PostgreSQL database support.

## Features

- **CRUD operations** for items (Create, Read, Update, Delete)
- **UUID-based identification** for each item
- **PostgreSQL database** with SQLAlchemy async ORM
- **Auto-generated API docs** at `/docs`

## Prerequisites

### Option 1: Docker (Recommended)
- Docker
- Docker Compose

### Option 2: Local Development
- Python 3.10+
- PostgreSQL 12+

## Setup

### Option A: Docker Setup (Recommended)

The easiest way to run the application is using Docker Compose:

```bash
# Build and start all services (API + PostgreSQL)
docker-compose up --build

# Or run in detached mode
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

The API will be available at `http://localhost:8000`

**Docker Services:**
- **API**: FastAPI application (port 8000)
- **Database**: PostgreSQL 15 (port 5432)
- **Volume**: Persistent storage for database data

### Option B: Local Development Setup

### 1. Install PostgreSQL

If you don't have PostgreSQL installed:

```bash
# macOS (using Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create the database
createdb items_db
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure Database

Copy `.env.example` to `.env` and update if needed:

```bash
cp .env.example .env
```

Default connection string:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/items_db
```

### 4. Run the Server

```bash
./venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### GET `/items`
List all items.

### GET `/items/{uuid}`
Get a specific item by UUID.

### POST `/items`
Create a new item (UUID auto-generated).

**Request body:**
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
  "item_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "item": {
    "name": "Widget",
    "description": "A great widget",
    "price": 19.99,
    "in_stock": true
  }
}
```

### PUT `/items/{uuid}`
Update an existing item.

### DELETE `/items/{uuid}`
Delete an item.

## Interactive API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Database Schema

### Items Table

| Column      | Type    | Description              |
|-------------|---------|--------------------------|
| id          | UUID    | Primary key (auto)       |
| name        | String  | Item name (required)     |
| description | Text    | Item description (optional) |
| price       | Float   | Item price (required)    |
| in_stock    | Boolean | Stock status (default: true) |

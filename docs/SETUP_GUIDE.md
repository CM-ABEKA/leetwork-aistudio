# AI Model Studio - Setup Guide

Complete guide to setting up the AI Model Studio development environment.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** 24+ and **Docker Compose**
- **Node.js** 18+ and npm 9+ (for local frontend development)
- **Python** 3.11+ (for local backend development)
- **Git** for version control
- **PostgreSQL client** (psql) for database management (optional)

## Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd leetwork-studio
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your preferred settings (optional for development)
# The default values work out of the box for local development
```

### 3. Start All Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps
```

### 4. Initialize Database

```bash
# Run database migrations
docker-compose exec postgres psql -U leetuser -d leetstudio -f /docker-entrypoint-initdb.d/001_initial_schema.sql

# (Optional) Load seed data
docker-compose exec postgres psql -U leetuser -d leetstudio -f /docker-entrypoint-initdb.d/seed_data.sql
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8002/docs
- **Auth Service API**: http://localhost:8001/docs
- **MinIO Console**: http://localhost:9001
  - Username: `minioadmin`
  - Password: `minioadmin123`

## Detailed Setup

### Service Architecture

The platform consists of multiple services:

1. **Frontend** (Next.js) - Port 3000
2. **Auth Service** (FastAPI) - Port 8001
3. **Orchestrator Service** (FastAPI) - Port 8002
4. **ML Classical Service** (FastAPI) - Port 8010
5. **PostgreSQL** - Port 5432
6. **Redis** - Port 6379
7. **MinIO** - Ports 9000 (API) & 9001 (Console)
8. **Celery Workers** (Background jobs)

### Development Workflow

#### Option A: Full Docker Development

All services run in Docker containers:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

#### Option B: Hybrid Development

Infrastructure in Docker, code running locally:

```bash
# Start only infrastructure services
docker-compose up -d postgres redis minio

# Run frontend locally
cd frontend
npm install
npm run dev

# Run backend services locally (separate terminals)
cd backend/auth-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

cd backend/orchestrator-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

### Database Management

#### Connect to PostgreSQL

```bash
# Via Docker
docker-compose exec postgres psql -U leetuser -d leetstudio

# Locally (if psql installed)
psql -h localhost -p 5432 -U leetuser -d leetstudio
# Password: test
```

#### Common Database Commands

```sql
-- List all tables
\dt

-- Describe table structure
\d users

-- View all users
SELECT * FROM users;

-- View project statistics
SELECT * FROM project_statistics;
```

#### Run Migrations

```bash
# Apply all migrations
docker-compose exec postgres psql -U leetuser -d leetstudio -f /docker-entrypoint-initdb.d/001_initial_schema.sql

# Reset database (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d postgres
```

### MinIO (Object Storage) Setup

#### Access MinIO Console

1. Navigate to http://localhost:9001
2. Login with `minioadmin` / `minioadmin123`
3. The `ml-platform` bucket is automatically created

#### Using MinIO CLI

```bash
# Install MinIO client
# macOS: brew install minio/stable/mc
# Linux: wget https://dl.min.io/client/mc/release/linux-amd64/mc

# Configure
mc alias set local http://localhost:9000 minioadmin minioadmin123

# List buckets
mc ls local

# Upload file
mc cp dataset.csv local/ml-platform/datasets/

# Download file
mc cp local/ml-platform/models/model.pkl ./
```

### Redis Management

#### Connect to Redis

```bash
# Via Docker
docker-compose exec redis redis-cli -a redis_dev_pass

# Check connection
PING  # Should return PONG

# View all keys
KEYS *

# Monitor real-time commands
MONITOR
```

### Frontend Development

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Available Scripts

```bash
# Development server (with hot reload)
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Type check
npm run type-check

# Format code
npm run format
```

#### Environment Variables

Frontend environment variables must be prefixed with `NEXT_PUBLIC_`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8002
NEXT_PUBLIC_WS_URL=ws://localhost:8002
```

### Backend Development

#### Python Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
cd backend/auth-service
pip install -r requirements.txt
```

#### Running Services

```bash
# Auth Service
cd backend/auth-service
uvicorn main:app --reload --port 8001

# Orchestrator Service
cd backend/orchestrator-service
uvicorn main:app --reload --port 8002
```

#### Testing APIs

All FastAPI services have auto-generated documentation:

- Auth Service: http://localhost:8001/docs
- Orchestrator Service: http://localhost:8002/docs

You can test endpoints directly from the Swagger UI.

### Celery Workers

#### Start Worker Locally

```bash
cd backend/orchestrator-service

# CPU worker
celery -A celery_app worker --loglevel=info -Q cpu_queue --concurrency=4

# With monitoring (Flower)
pip install flower
celery -A celery_app flower
# Access at http://localhost:5555
```

#### Monitor Tasks

```bash
# List active tasks
celery -A celery_app inspect active

# List registered tasks
celery -A celery_app inspect registered

# Purge all tasks
celery -A celery_app purge
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Check what's using a port
# On Windows:
netstat -ano | findstr :3000

# On macOS/Linux:
lsof -i :3000

# Kill the process
kill -9 <PID>
```

#### Docker Container Won't Start

```bash
# View logs
docker-compose logs <service-name>

# Rebuild and start
docker-compose up -d --build <service-name>

# Remove all containers and volumes
docker-compose down -v
docker-compose up -d
```

#### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

#### Frontend Build Errors

```bash
# Clear Next.js cache
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

### Reset Everything

```bash
# Stop all containers and remove volumes
docker-compose down -v

# Remove all Docker images
docker-compose down --rmi all

# Start fresh
docker-compose up -d --build
```

## Next Steps

After successful setup:

1. **Test Authentication**: Visit http://localhost:3000 and try to register
2. **Explore API Docs**: Check out http://localhost:8002/docs
3. **Read the Master Plan**: See [CLAUD_AISTUDIO_PLAN.md](../CLAUD_AISTUDIO_PLAN.md)
4. **Start Development**: Follow the [Development Guide](./DEVELOPMENT_GUIDE.md)

## Need Help?

- Check the [FAQ](./FAQ.md)
- Review [API Documentation](./API_REFERENCE.md)
- Read the [Architecture Guide](./ARCHITECTURE.md)
- File an issue on GitHub

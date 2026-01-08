# AI Model Studio Platform

> Transform raw data into production-ready AI models without writing a single line of code.

## Overview

AI Model Studio is a comprehensive, cloud-agnostic AI/ML platform that democratizes artificial intelligence by enabling users without extensive technical skills to upload and clean datasets, train models across 13 AI domains, evaluate performance, and deploy trained models through an intuitive interface.

## Features

### Current (MVP - Phase 0)
- 🏗️ **Foundation Infrastructure**: Docker-based microservices architecture
- 🔐 **Authentication**: JWT-based auth system
- 📊 **Classical ML**: Classification, Regression, Clustering
- 📝 **NLP**: Text classification, Sentiment analysis
- 🧹 **Data Cleaning**: Intelligent data quality detection and cleaning

### Planned (Full Vision)
- 🤖 **13 AI Domains**: ML, NLP, Computer Vision, Time Series, Audio, RL, Graph AI, Robotics, GenAI, Synthetic Data, MLOps, Edge AI, Governance
- 🎯 **47 Specialized Modules**: Complete AI ecosystem
- 📈 **AutoML**: Automated algorithm selection and hyperparameter tuning
- 🔍 **Explainability**: SHAP, LIME, feature importance
- 🚀 **Model Deployment**: One-click API deployment

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER BROWSER                         │
│                    (React/Next.js Frontend)                  │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS/WSS
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                     API GATEWAY / NGINX                      │
└────────┬────────────────────────────────────────────────┬───┘
         │                                                 │
         ↓                                                 ↓
┌────────────────────┐                          ┌─────────────────┐
│   FRONTEND SERVER  │                          │  BACKEND APIs   │
│   (Next.js SSR)    │                          │  (FastAPI x13)  │
└────────┬───────────┘                          └────────┬────────┘
         │                                                │
         ↓                                                ↓
┌────────────────────────────────────────────────────────────────┐
│                      SHARED SERVICES LAYER                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │PostgreSQL│  │  Redis   │  │  MinIO   │  │  Celery  │      │
│  │(Metadata)│  │ (Queue)  │  │(Storage) │  │ (Workers)│      │
└────────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Frontend
- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 4 + Shadcn UI
- **State**: React Context, TanStack Query, Zustand
- **Charts**: Recharts, D3.js

### Backend
- **Framework**: FastAPI 0.100+
- **Language**: Python 3.11+
- **Task Queue**: Celery 5.3+ with Redis
- **ML Libraries**: Scikit-learn, PyTorch, TensorFlow, Transformers, XGBoost

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Database**: PostgreSQL 16+
- **Cache/Queue**: Redis 7+
- **Object Storage**: MinIO (S3-compatible)
- **Monitoring**: Prometheus, Grafana

## Project Structure

```
leetwork-studio/
├── docker-compose.yml              # Main Docker Compose configuration
├── docker-compose.prod.yml         # Production configuration
├── .env.example                    # Environment variables template
├── frontend/                       # Next.js frontend application
├── backend/
│   ├── shared/                    # Shared utilities and models
│   ├── auth-service/              # Authentication service
│   ├── orchestrator-service/      # Main API orchestrator
│   ├── ml-classical-service/      # Classical ML engine
│   ├── ml-nlp-service/            # NLP engine
│   └── [11 more ML services...]   # Other domain services
├── database/
│   ├── migrations/                # SQL migration scripts
│   └── seed_data.sql              # Sample data for development
├── infrastructure/
│   ├── nginx/                     # Nginx configuration
│   ├── monitoring/                # Prometheus & Grafana configs
│   └── terraform/                 # Infrastructure as Code
├── docs/                          # Documentation
└── tests/                         # Test suites
```

## Quick Start

### Prerequisites
- Docker 24+ and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd leetwork-studio
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (default values work for development)
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Check service status**
   ```bash
   docker-compose ps
   ```

5. **Initialize the database**
   ```bash
   docker-compose exec postgres psql -U leetuser -d leetstudio -f /docker-entrypoint-initdb.d/001_initial_schema.sql
   ```

6. **View logs (optional)**
   ```bash
   # All services
   docker-compose logs -f

   # Specific service
   docker-compose logs -f frontend
   docker-compose logs -f orchestrator-service
   docker-compose logs -f auth-service
   ```

7. **Access the application**
   - **Frontend**: http://localhost:3005
   - **API Documentation (Orchestrator)**: http://localhost:8002/docs
   - **Auth Service API**: http://localhost:8001/docs
   - **MinIO Console**: http://localhost:9001
     - Username: `minioadmin`
     - Password: `minioadmin123`
   - **Prometheus**: http://localhost:9090 (if enabled)
   - **Grafana**: http://localhost:3001 (if enabled)

### Verify Services

**Test API endpoints:**
```bash
# Test orchestrator service
curl http://localhost:8002/

# Test auth service health
curl http://localhost:8001/health
```

**Check database connection:**
```bash
docker-compose exec postgres psql -U leetuser -d leetstudio -c "SELECT COUNT(*) FROM users;"
```

### Troubleshooting

**If services fail to start:**
```bash
# View error logs for a specific service
docker-compose logs [service-name]

# Rebuild and restart all services
docker-compose down
docker-compose up -d --build
```

**To stop all services:**
```bash
docker-compose down
```

**To stop and remove all data (full reset):**
```bash
docker-compose down -v
```

**Port conflicts:**
```bash
# Check if ports are already in use
# Windows:
netstat -ano | findstr :3005
netstat -ano | findstr :8002

# Linux/Mac:
lsof -i :3005
lsof -i :8002
```

## Development

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend/orchestrator-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

### Running Tests
```bash
# Frontend tests
cd frontend && npm test

# Backend tests
cd backend && pytest
```

## Roadmap

### Phase 0: Foundation ✅ (Weeks 1-2)
- [x] Project setup and infrastructure
- [x] Docker Compose configuration
- [x] Database schema

### Phase 1: Authentication & Core UI (Weeks 3-4)
- [ ] User registration and login
- [ ] Dashboard layout
- [ ] Protected routes

### Phase 2: Classical ML Domain (Weeks 5-8) - **MVP**
- [ ] Data upload and cleaning
- [ ] Model training (Logistic Regression, Random Forest, XGBoost)
- [ ] Evaluation and metrics
- [ ] Model download

### Phase 3-12: Full Vision (Months 3-12)
- [ ] Additional AI domains (NLP, Vision, Audio, etc.)
- [ ] AutoML and explainability
- [ ] Model deployment and serving
- [ ] Production optimization

See [CLAUD_AISTUDIO_PLAN.md](../CLAUD_AISTUDIO_PLAN.md) for the complete roadmap.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Guidelines
- Follow TypeScript/Python best practices
- Write tests for new features
- Update documentation
- Use conventional commits

## Documentation

- [Master Plan](../CLAUD_AISTUDIO_PLAN.md) - Complete project specification
- [Architecture](./docs/architecture.md) - System architecture details
- [API Reference](./docs/api-reference.md) - API documentation
- [User Guide](./docs/user-guide.md) - End-user documentation
- [Deployment](./docs/deployment.md) - Deployment instructions

## License

[Your chosen license]

## Support

- Documentation: [Link to docs]
- Issues: [GitHub Issues]
- Discussions: [GitHub Discussions]
- Email: support@example.com

---

**Built with ❤️ to democratize AI for everyone**

*Current Version: 0.1.0 (Phase 0 - Foundation)*

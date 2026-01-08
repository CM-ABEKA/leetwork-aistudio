# Development Guide

Guide for developers working on the AI Model Studio platform.

## Project Structure

```
leetwork-studio/
├── frontend/                    # Next.js frontend application
│   ├── src/
│   │   ├── app/                # Next.js App Router pages
│   │   ├── components/         # React components
│   │   └── lib/                # Utilities, hooks, types
│   ├── public/                 # Static assets
│   ├── package.json
│   └── Dockerfile
├── backend/                     # Python backend services
│   ├── auth-service/           # Authentication & JWT
│   ├── orchestrator-service/   # Main API gateway
│   ├── ml-classical-service/   # Classical ML engine
│   └── shared/                 # Shared utilities
├── database/
│   ├── migrations/             # SQL migration scripts
│   └── seed_data.sql           # Sample data
├── infrastructure/
│   ├── nginx/                  # Reverse proxy config
│   ├── monitoring/             # Prometheus & Grafana
│   └── terraform/              # IaC templates
├── docs/                        # Documentation
├── tests/                       # Test suites
├── docker-compose.yml          # Development environment
└── .env.example                # Environment template
```

## Development Workflow

### 1. Pick a Task

Tasks are tracked in the Phase checklist (see README.md). Current focus: **Phase 0 - Foundation** ✅

Next: **Phase 1 - Authentication & Core UI** (Weeks 3-4)

### 2. Create a Feature Branch

```bash
git checkout -b feature/user-authentication
git checkout -b fix/database-connection
git checkout -b docs/api-reference
```

### 3. Make Changes

Follow the coding standards and best practices outlined below.

### 4. Test Your Changes

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend/auth-service
pytest

# Integration tests
# TODO: Set up integration tests
```

### 5. Commit and Push

```bash
git add .
git commit -m "feat: implement user registration endpoint"
git push origin feature/user-authentication
```

### 6. Create Pull Request

- Provide clear description of changes
- Reference related issues
- Ensure CI/CD checks pass
- Request code review

## Coding Standards

### Frontend (TypeScript/React)

#### File Naming
- Components: `PascalCase.tsx` (e.g., `UserProfile.tsx`)
- Utilities: `camelCase.ts` (e.g., `formatDate.ts`)
- Hooks: `use*.ts` (e.g., `useAuth.ts`)
- Types: `PascalCase.ts` (e.g., `User.ts`)

#### Component Structure
```typescript
// Imports
import { useState } from 'react';
import { Button } from '@/components/ui/button';

// Types/Interfaces
interface UserProfileProps {
  userId: string;
}

// Component
export function UserProfile({ userId }: UserProfileProps) {
  // Hooks
  const [data, setData] = useState(null);

  // Functions
  const handleClick = () => {
    // ...
  };

  // Render
  return (
    <div>
      {/* JSX */}
    </div>
  );
}
```

#### TypeScript Rules
- Always use TypeScript, never `any`
- Define interfaces for props and data structures
- Use strict mode
- Enable all linting rules

### Backend (Python/FastAPI)

#### File Naming
- Modules: `snake_case.py` (e.g., `user_service.py`)
- Classes: `PascalCase` (e.g., `UserService`)
- Functions: `snake_case` (e.g., `create_user`)

#### Code Structure
```python
"""
Module docstring explaining purpose
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Router
router = APIRouter(prefix="/api/v1/users")

# Models
class UserCreate(BaseModel):
    """Create user request model"""
    email: str
    password: str

# Endpoints
@router.post("/")
async def create_user(user: UserCreate):
    """
    Create a new user

    Args:
        user: User creation data

    Returns:
        Created user object

    Raises:
        HTTPException: If user already exists
    """
    # Implementation
    pass
```

#### Python Rules
- Follow PEP 8 style guide
- Use type hints everywhere
- Write docstrings for all functions/classes
- Use async/await for I/O operations
- Handle errors explicitly

### Database

#### Migration Scripts
- Prefix with number: `001_initial_schema.sql`, `002_add_indexes.sql`
- Include rollback instructions in comments
- Test on development database first

#### Naming Conventions
- Tables: `snake_case` (e.g., `training_jobs`)
- Columns: `snake_case` (e.g., `created_at`)
- Indexes: `idx_table_column` (e.g., `idx_users_email`)
- Foreign keys: `fk_table_reftable` (e.g., `fk_projects_users`)

### API Design

#### REST Principles
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Return appropriate status codes
- Use consistent error format
- Version your APIs (`/api/v1/...`)

#### URL Structure
```
GET    /api/v1/projects           # List resources
POST   /api/v1/projects           # Create resource
GET    /api/v1/projects/:id       # Get single resource
PUT    /api/v1/projects/:id       # Update resource
DELETE /api/v1/projects/:id       # Delete resource
GET    /api/v1/projects/:id/jobs  # Nested resources
```

#### Response Format
```json
{
  "id": "uuid",
  "name": "Project Name",
  "created_at": "2026-01-08T12:00:00Z",
  "status": "active"
}
```

#### Error Format
```json
{
  "error": "Resource not found",
  "code": "NOT_FOUND",
  "details": {
    "resource": "project",
    "id": "abc-123"
  }
}
```

## Git Workflow

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add user authentication endpoint
fix: resolve database connection issue
docs: update API documentation
style: format code with prettier
refactor: restructure project service
test: add unit tests for auth service
chore: update dependencies
```

### Branch Naming

```
feature/feature-name
fix/bug-description
docs/documentation-update
refactor/code-improvement
test/test-addition
```

## Testing

### Frontend Testing

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

#### Test Structure
```typescript
import { render, screen } from '@testing-library/react';
import { UserProfile } from './UserProfile';

describe('UserProfile', () => {
  it('renders user name', () => {
    render(<UserProfile userId="123" />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
```

### Backend Testing

```bash
cd backend/auth-service

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_create_user
```

#### Test Structure
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/register", json={
        "email": "test@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 201
    assert "access_token" in response.json()
```

## Debugging

### Frontend Debugging

#### Browser DevTools
- Use React DevTools extension
- Check Network tab for API calls
- Use Console for errors

#### VS Code Configuration
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug client-side",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000"
    }
  ]
}
```

### Backend Debugging

#### Python Debugger
```python
import pdb; pdb.set_trace()  # Set breakpoint
```

#### FastAPI Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"User created: {user.email}")
```

#### Docker Logs
```bash
# View service logs
docker-compose logs -f orchestrator-service

# View last 100 lines
docker-compose logs --tail=100 auth-service
```

## Performance

### Frontend Optimization
- Use React.memo() for expensive components
- Implement lazy loading for routes
- Optimize images with Next.js Image component
- Use server-side rendering where appropriate

### Backend Optimization
- Use database indexes effectively
- Implement caching with Redis
- Use async operations for I/O
- Profile slow endpoints with timing logs

### Database Optimization
- Create indexes for frequently queried columns
- Use EXPLAIN ANALYZE for slow queries
- Implement connection pooling
- Use pagination for large result sets

## Security

### Frontend Security
- Never store sensitive data in localStorage
- Sanitize user inputs
- Use HTTPS in production
- Implement CSRF protection

### Backend Security
- Validate all inputs with Pydantic
- Use parameterized SQL queries
- Hash passwords with bcrypt
- Implement rate limiting
- Keep dependencies updated

### API Security
- Require authentication for protected endpoints
- Use JWT tokens with short expiry
- Implement role-based access control
- Log security events

## Documentation

### Code Documentation
- Write clear docstrings/JSDoc comments
- Document complex algorithms
- Explain "why" not just "what"
- Keep README files up-to-date

### API Documentation
- Use OpenAPI/Swagger specifications
- Provide example requests/responses
- Document error codes
- Include authentication requirements

## Tools & IDE Setup

### VS Code Extensions
- **Frontend**:
  - ESLint
  - Prettier
  - TypeScript and JavaScript Language Features
  - Tailwind CSS IntelliSense
- **Backend**:
  - Python
  - Pylance
  - Python Docstring Generator
- **General**:
  - Docker
  - GitLens
  - REST Client

### VS Code Settings
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black"
}
```

## Common Tasks

### Adding a New API Endpoint
1. Define request/response models (Pydantic)
2. Implement endpoint logic
3. Add authentication if required
4. Write unit tests
5. Update API documentation
6. Test with Swagger UI

### Adding a New Frontend Page
1. Create page file in `src/app/`
2. Design component structure
3. Implement data fetching
4. Add error handling
5. Style with Tailwind CSS
6. Write tests
7. Update navigation

### Adding a Database Table
1. Write migration SQL script
2. Add SQLAlchemy model (if using ORM)
3. Create Pydantic schemas
4. Test migration locally
5. Update seed data if needed
6. Document in schema docs

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

## Questions?

If you have questions about development:
1. Check this guide first
2. Search existing issues on GitHub
3. Ask in team discussions
4. Create a new issue if needed

---
init:
  commands:
    - "django-admin startproject config ."
    - "python manage.py startapp <app_name>"
    - "pip install -r requirements.txt"
  description: "Initialize Django project and install dependencies"

dev:
  commands:
    - "python manage.py runserver"
  description: "Start development server on http://127.0.0.1:8000"

test:
  commands:
    - "pytest"
    - "python manage.py test"
  description: "Run tests with pytest or Django test runner"
  coverage: "pytest --cov=apps --cov-report=html"

build:
  commands:
    - "python manage.py collectstatic --noinput"
  description: "Collect static files for production"

migrate:
  commands:
    - "python manage.py makemigrations"
    - "python manage.py migrate"
  description: "Create and apply database migrations"

lint:
  commands:
    - "ruff check ."
    - "flake8 apps/"
  description: "Run linter checks"

format:
  commands:
    - "ruff format ."
    - "black apps/"
  description: "Format code"

deploy:
  commands:
    - "gunicorn config.wsgi:application --bind 0.0.0.0:8000"
  description: "Run production server with Gunicorn"

monitoring:
  admin: "http://localhost:8000/admin/"
  api: "http://localhost:8000/api/"
---

# Automation Profile — Django

## Development Workflow

### 1. Initial Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Django
pip install django djangorestframework

# Create project
django-admin startproject config .

# Create apps
python manage.py startapp users
python manage.py startapp core

# Install dependencies
pip install -r requirements.txt

# requirements.txt example:
# django>=5.0
# djangorestframework>=3.14
# psycopg2-binary>=2.9  # PostgreSQL
# celery>=5.3
# redis>=5.0
# django-environ>=0.11
# gunicorn>=21.2
# pytest-django>=4.5
# ruff>=0.1
```

### 2. Database Setup

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Dump data (backup)
python manage.py dumpdata > backup.json

# Load data (restore)
python manage.py loaddata backup.json

# Reset database
python manage.py flush

# Show migrations
python manage.py showmigrations

# SQL for migration
python manage.py sqlmigrate app_name migration_number
```

### 3. Development Server

```bash
# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080

# Run on all interfaces
python manage.py runserver 0.0.0.0:8000

# With settings override
python manage.py runserver --settings=config.settings.development
```

### 4. Django Shell

```bash
# Interactive Python shell with Django
python manage.py shell

# Shell Plus (django-extensions)
pip install django-extensions
python manage.py shell_plus

# Example usage:
# >>> from apps.users.models import User
# >>> User.objects.all()
# >>> user = User.objects.create_user('test', 'test@example.com', 'pass')
```

### 5. Testing

```bash
# Run all tests (Django test runner)
python manage.py test

# Run specific app tests
python manage.py test apps.users

# Run specific test class
python manage.py test apps.users.tests.UserModelTest

# Run with pytest
pytest

# With coverage
pytest --cov=apps --cov-report=html
coverage report

# Parallel testing
pytest -n auto

# Keep database between runs (faster)
pytest --reuse-db

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### 6. Static Files

```bash
# Collect static files
python manage.py collectstatic

# No input prompt
python manage.py collectstatic --noinput

# Clear existing files first
python manage.py collectstatic --clear --noinput

# Find static files
python manage.py findstatic admin/css/base.css
```

### 7. Database Queries & Debugging

```bash
# Show SQL queries for a command
python manage.py migrate --verbosity=3

# Django Debug Toolbar (install: pip install django-debug-toolbar)
# Add to INSTALLED_APPS and middleware in settings.py

# Log all SQL queries in shell
from django.db import connection
from django.db import reset_queries

reset_queries()
# ... your ORM queries ...
print(len(connection.queries))  # Number of queries
print(connection.queries)  # Actual SQL
```

### 8. Management Commands

```bash
# Create custom management command
# apps/users/management/commands/create_test_users.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Create test users'

    def handle(self, *args, **options):
        # command logic
        self.stdout.write(self.style.SUCCESS('Users created'))

# Run custom command
python manage.py create_test_users

# List all commands
python manage.py help
```

### 9. Celery (Async Tasks)

```bash
# Start Celery worker
celery -A config worker --loglevel=info

# Start Celery beat (scheduler)
celery -A config beat --loglevel=info

# Both worker and beat
celery -A config worker --beat --loglevel=info

# Flower (monitoring tool)
pip install flower
celery -A config flower

# Purge all tasks
celery -A config purge
```

### 10. Production Deployment

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

# Check deployment readiness
python manage.py check --deploy

# Run with Gunicorn
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -

# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
```

### 11. Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: celery -A config worker --loglevel=info
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

```bash
# Docker commands
docker-compose up --build
docker-compose run web python manage.py migrate
docker-compose run web python manage.py createsuperuser
docker-compose down
```

### 12. Linting & Formatting

```bash
# Ruff (modern, fast linter)
pip install ruff

# Check code
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code
ruff format .

# Black (code formatter)
pip install black
black apps/

# Flake8 (linter)
pip install flake8
flake8 apps/

# isort (import sorting)
pip install isort
isort apps/

# mypy (type checking)
pip install mypy django-stubs
mypy apps/
```

### 13. Environment Variables

```bash
# .env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
CELERY_BROKER_URL=redis://localhost:6379/0

# settings.py
import environ

env = environ.Env()
environ.Env.read_env()

DEBUG = env.bool('DEBUG', default=False)
SECRET_KEY = env('SECRET_KEY')
DATABASES = {'default': env.db('DATABASE_URL')}
```

## CI/CD Pipeline Example

```yaml
# .github/workflows/django.yml
name: Django CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run migrations
        run: python manage.py migrate
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/testdb

      - name: Run tests
        run: pytest --cov=apps
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/testdb

      - name: Lint
        run: ruff check .
```

## Quality Gates

- ✅ All tests pass (`pytest`)
- ✅ Code coverage ≥ 80% (`pytest --cov`)
- ✅ Linter passes (`ruff check .`)
- ✅ Migrations created and applied (`python manage.py migrate`)
- ✅ Security check (`python manage.py check --deploy`)
- ✅ No N+1 queries (use django-debug-toolbar)

## Useful Commands

```bash
# Show URLs
python manage.py show_urls  # django-extensions

# Database shell
python manage.py dbshell

# Clear cache
python manage.py clear_cache  # django-extensions

# Generate secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Check for issues
python manage.py check

# Validate models
python manage.py validate  # deprecated, use check

# Create app
python manage.py startapp app_name

# Squash migrations
python manage.py squashmigrations app_name 0001 0005

# Fake migration (mark as applied without running)
python manage.py migrate app_name 0001 --fake
```

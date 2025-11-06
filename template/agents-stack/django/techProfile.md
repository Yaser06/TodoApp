---
language: "Python"
version: "3.11+"
framework: "Django"
frameworkVersion: "5.0+"
packageManager: "pip / poetry / pipenv"
keyLibraries:
  - "djangorestframework (DRF for APIs)"
  - "celery (async task queue)"
  - "redis (caching & Celery broker)"
  - "psycopg2 or psycopg3 (PostgreSQL driver)"
  - "django-environ (environment variables)"
  - "gunicorn (WSGI server)"
architecture: "MVT (Model-View-Template)"
testFramework: "pytest-django / unittest"
buildTool: "python manage.py"
linting: "ruff / flake8"
---

# Tech Profile — Django

## Core Stack

**Language**: Python 3.11+
**Framework**: Django 5.0+
**API Framework**: Django REST Framework (DRF)
**Database**: PostgreSQL (recommended), MySQL, SQLite
**Caching**: Redis, Memcached
**Task Queue**: Celery + Redis/RabbitMQ
**WSGI Server**: Gunicorn, uWSGI

## Project Structure

```
project/
├── manage.py
├── config/                    # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                      # Django apps
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py     # DRF serializers
│   │   ├── urls.py
│   │   └── tests/
│   └── core/
├── static/                    # Static files
├── media/                     # User uploads
├── templates/                 # HTML templates
├── requirements.txt
└── .env                       # Environment variables
```

## Django Settings Pattern

```python
# config/settings.py
from pathlib import Path
import environ

env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

DATABASES = {
    'default': env.db('DATABASE_URL')
}

# Separate settings files
# config/settings/base.py, config/settings/development.py, config/settings/production.py
```

## Models & ORM

```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.email

# Query optimization
# Bad: N+1 problem
for user in User.objects.all():
    print(user.profile.bio)  # Hits DB each time

# Good: select_related (1-to-1, ForeignKey)
for user in User.objects.select_related('profile').all():
    print(user.profile.bio)  # Single query

# Good: prefetch_related (Many-to-Many, reverse FK)
for user in User.objects.prefetch_related('posts').all():
    for post in user.posts.all():
        print(post.title)
```

## Django REST Framework

```python
# serializers.py
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'created_at']
        read_only_fields = ['id', 'created_at']

# views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'user activated'})

# urls.py
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = router.urls
```

## Celery for Async Tasks

```python
# config/celery.py
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_welcome_email(user_id):
    user = User.objects.get(id=user_id)
    send_mail(
        'Welcome!',
        'Thanks for signing up.',
        'from@example.com',
        [user.email],
    )
```

## Caching

```python
from django.core.cache import cache
from django.views.decorators.cache import cache_page

# Cache for 5 minutes
@cache_page(60 * 5)
def my_view(request):
    # expensive operation
    return render(request, 'template.html')

# Manual caching
def get_user_data(user_id):
    key = f'user_data_{user_id}'
    data = cache.get(key)
    if data is None:
        data = User.objects.get(id=user_id)
        cache.set(key, data, 60 * 15)  # 15 minutes
    return data
```

## Authentication

```python
# JWT with djangorestframework_simplejwt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Custom permissions
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
```

## Testing

```python
# tests/test_models.py
import pytest
from apps.users.models import User

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')

# tests/test_api.py
from rest_framework.test import APITestCase
from rest_framework import status

class UserAPITestCase(APITestCase):
    def test_create_user(self):
        url = '/api/users/'
        data = {'username': 'newuser', 'email': 'new@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

## Production Deployment

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5

# Run with
# gunicorn config.wsgi:application -c gunicorn.conf.py
```

## Environment Variables

```bash
# .env
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgres://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=example.com,www.example.com
CELERY_BROKER_URL=redis://localhost:6379/0
```

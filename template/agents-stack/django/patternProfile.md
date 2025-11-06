---
architectureStyle: "MVT (Model-View-Template)"
layering: "URL → View → Model → Template"
errorStrategy: "exceptions with custom error handlers"
testingApproach: "pytest-django with fixtures"
observability: "logging + django-debug-toolbar (dev)"
---

# Pattern Profile — Django

## Architecture Pattern: MVT (Model-View-Template)

```
┌─────────────────────────────────────┐
│            URL Router               │  ← urls.py maps URLs to views
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│             Views                   │  ← Business logic & orchestration
│  (Function-based or Class-based)    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│            Models                   │  ← Data layer (ORM)
│  (Business logic in model methods)  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│          Templates                  │  ← Presentation (HTML)
│  (Django template language)         │
└─────────────────────────────────────┘
```

## View Patterns

### Function-Based Views (FBVs)

**Best for**: Simple logic, straightforward request handling

```python
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Post

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'posts/detail.html', {'post': post})

def post_list_json(request):
    posts = Post.objects.all()
    data = [{'id': p.id, 'title': p.title} for p in posts]
    return JsonResponse({'posts': data})
```

### Class-Based Views (CBVs)

**Best for**: Complex logic, reusable patterns

```python
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

class PostListView(ListView):
    model = Post
    template_name = 'posts/list.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        return Post.objects.select_related('author').filter(published=True)

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'posts/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
```

## Model Patterns

### Fat Models, Thin Views

**Keep business logic in models:**

```python
from django.db import models
from django.utils import timezone

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-published_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        """Business logic in model"""
        return self.published_at is not None and self.published_at <= timezone.now()

    def publish(self):
        """Domain method"""
        if not self.is_published:
            self.published_at = timezone.now()
            self.save(update_fields=['published_at'])

    def unpublish(self):
        """Domain method"""
        self.published_at = None
        self.save(update_fields=['published_at'])

# Usage in view (thin view)
def publish_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()  # Business logic in model
    return redirect('post-detail', pk=post.pk)
```

### Custom Managers

```python
from django.db import models

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published_at__isnull=False)

class Post(models.Model):
    # fields...

    objects = models.Manager()  # Default manager
    published = PublishedManager()  # Custom manager

# Usage
Post.objects.all()  # All posts
Post.published.all()  # Only published posts
```

## Form Patterns

### Model Forms

```python
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

    def clean_title(self):
        """Custom validation"""
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters")
        return title

# Usage in view
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post-detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'posts/create.html', {'form': form})
```

## Django REST Framework Patterns

### Viewsets Pattern

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filter queryset based on request"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(published_at__isnull=False)
        return queryset

    def perform_create(self, serializer):
        """Custom save logic"""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Custom action"""
        post = self.get_object()
        post.publish()
        return Response({'status': 'published'})
```

### Serializer Patterns

```python
from rest_framework import serializers

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    is_published = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'is_published', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_title(self, value):
        """Field-level validation"""
        if len(value) < 5:
            raise serializers.ValidationError("Title too short")
        return value

    def validate(self, data):
        """Object-level validation"""
        if 'spam' in data.get('content', '').lower():
            raise serializers.ValidationError("Spam detected")
        return data
```

## Signals Pattern

**Decouple side effects:**

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

@receiver(post_save, sender=Post)
def notify_on_publish(sender, instance, created, **kwargs):
    """Send notification when post is published"""
    if not created and instance.is_published:
        send_mail(
            'New Post Published',
            f'{instance.title} is now live!',
            'from@example.com',
            ['admin@example.com'],
        )
```

## Middleware Pattern

```python
# middleware.py
class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Before view
        print(f"Request: {request.method} {request.path}")

        response = self.get_response(request)

        # After view
        print(f"Response: {response.status_code}")
        return response

# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'myapp.middleware.RequestLoggingMiddleware',  # Custom
    # ... other middleware
]
```

## Service Layer Pattern (Optional)

**For complex business logic:**

```python
# services.py
class PostService:
    @staticmethod
    def publish_post(post_id, user):
        """Complex business logic in service layer"""
        post = Post.objects.get(id=post_id)

        if not user.has_perm('posts.publish_post'):
            raise PermissionError("User cannot publish posts")

        post.publish()

        # Send notifications
        notify_subscribers(post)

        # Update analytics
        update_analytics(post)

        return post

# views.py
from .services import PostService

def publish_post_view(request, pk):
    try:
        post = PostService.publish_post(pk, request.user)
        return JsonResponse({'status': 'success', 'post_id': post.id})
    except PermissionError as e:
        return JsonResponse({'error': str(e)}, status=403)
```

## Testing Patterns

### Fixtures

```python
# conftest.py
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def post(db, user):
    return Post.objects.create(
        title='Test Post',
        content='Test content',
        author=user
    )

# test_models.py
@pytest.mark.django_db
def test_post_publish(post):
    assert not post.is_published
    post.publish()
    assert post.is_published
```

### API Testing

```python
from rest_framework.test import APIClient
import pytest

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_post_list(api_client, post):
    response = api_client.get('/api/posts/')
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
def test_create_post(api_client, user):
    api_client.force_authenticate(user=user)
    data = {'title': 'New Post', 'content': 'New content'}
    response = api_client.post('/api/posts/', data)
    assert response.status_code == 201
    assert Post.objects.count() == 1
```

## Anti-Patterns to Avoid

❌ **Business Logic in Views**: Keep views thin, move logic to models/services
❌ **N+1 Queries**: Always use select_related/prefetch_related
❌ **Raw SQL Without Reason**: Use ORM unless performance critical
❌ **Signals for Everything**: Use sparingly, prefer explicit calls
❌ **God Models**: Split large models into related models
❌ **Hardcoded URLs**: Always use reverse() or {% url %} tag
❌ **Settings in Code**: Use environment variables
❌ **Large Serializers**: Split into nested serializers

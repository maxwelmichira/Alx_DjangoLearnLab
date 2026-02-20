from django.urls import path
from .views import (
    BookListView,
    BookDetailView,
    BookCreateView,
    BookUpdateView,
    BookDeleteView
)

urlpatterns = [
    # List all books - GET /books/
    path('books/', BookListView.as_view(), name='book-list'),
    
    # Create a new book - POST /books/create/
    path('books/create/', BookCreateView.as_view(), name='book-create'),
    
    # Retrieve a single book by ID - GET /books/<int:pk>/
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    
    # Update an existing book - PUT/PATCH /books/update/<int:pk>/
    path('books/update/<int:pk>/', BookUpdateView.as_view(), name='book-update'),
    
    # Delete a book - DELETE /books/delete/<int:pk>/
    path('books/delete/<int:pk>/', BookDeleteView.as_view(), name='book-delete'),
]

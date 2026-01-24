"""
Secure views for the bookshelf application.

Security features implemented:
- Permission-based access control
- CSRF protection (automatic with Django)
- SQL injection prevention (using Django ORM)
- Input validation through Django forms
- XSS prevention (Django auto-escapes template variables)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from .models import Book
from .forms import BookForm
from .forms import ExampleForm


# SECURITY: Using Django ORM prevents SQL injection
# All queries are parameterized automatically
@permission_required('bookshelf.can_view', raise_exception=True)
def book_list(request):
    """
    Display a list of all books.
    
    Security:
    - Requires 'can_view' permission
    - Uses ORM (prevents SQL injection)
    - Auto-escapes output in template (prevents XSS)
    """
    books = Book.objects.all()  # Secure: ORM parameterizes queries
    return render(request, 'bookshelf/book_list.html', {'books': books})


@permission_required('bookshelf.can_create', raise_exception=True)
def book_create(request):
    """
    Create a new book using secure Django forms.
    
    Security:
    - Requires 'can_create' permission
    - Uses Django ModelForm for validation
    - CSRF token required in template
    - Input sanitization through form.clean_*() methods
    """
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():  # Validates and sanitizes input
            form.save()  # Secure: ORM prevents SQL injection
            messages.success(request, 'Book created successfully!')
            return redirect('book_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm()
    
    return render(request, 'bookshelf/book_form.html', {
        'form': form,
        'action': 'Create'
    })


@permission_required('bookshelf.can_edit', raise_exception=True)
def book_edit(request, pk):
    """
    Edit an existing book using secure Django forms.
    
    Security:
    - Requires 'can_edit' permission
    - Uses get_object_or_404 to prevent information leakage
    - Form validation prevents malicious input
    - ORM prevents SQL injection
    """
    book = get_object_or_404(Book, pk=pk)  # Secure: parameterized query
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm(instance=book)
    
    return render(request, 'bookshelf/book_form.html', {
        'form': form,
        'book': book,
        'action': 'Edit'
    })


@permission_required('bookshelf.can_delete', raise_exception=True)
def book_delete(request, pk):
    """
    Delete a book with confirmation.
    
    Security:
    - Requires 'can_delete' permission
    - Requires POST request (prevents CSRF)
    - Uses get_object_or_404 to prevent information leakage
    """
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book_list')
    
    return render(request, 'bookshelf/book_confirm_delete.html', {'book': book})


def form_example_view(request):
    """
    Example view demonstrating secure form handling.
    
    Security features:
    - CSRF protection (automatic)
    - Input validation and sanitization
    - XSS prevention through auto-escaping
    """
    if request.method == 'POST':
        form = ExampleForm(request.POST)
        if form.is_valid():
            # Process the validated and sanitized data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            messages.success(request, f'Thank you, {name}! Your message has been received.')
            return redirect('form_example')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ExampleForm()
    
    return render(request, 'bookshelf/form_example.html', {'form': form})

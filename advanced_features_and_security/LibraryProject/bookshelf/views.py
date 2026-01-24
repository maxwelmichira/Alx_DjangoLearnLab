from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from .models import Book

# View to list all books - requires can_view permission
@permission_required('bookshelf.can_view', raise_exception=True)
def book_list(request):
    """
    Display a list of all books.
    Requires: bookshelf.can_view permission
    """
    books = Book.objects.all()
    return render(request, 'bookshelf/book_list.html', {'books': books})

# View to create a new book - requires can_create permission
@permission_required('bookshelf.can_create', raise_exception=True)
def book_create(request):
    """
    Create a new book.
    Requires: bookshelf.can_create permission
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        publication_year = request.POST.get('publication_year')
        
        if title and author and publication_year:
            Book.objects.create(
                title=title,
                author=author,
                publication_year=int(publication_year)
            )
            messages.success(request, 'Book created successfully!')
            return redirect('book_list')
        else:
            messages.error(request, 'All fields are required!')
    
    return render(request, 'bookshelf/book_form.html', {'action': 'Create'})

# View to edit an existing book - requires can_edit permission
@permission_required('bookshelf.can_edit', raise_exception=True)
def book_edit(request, pk):
    """
    Edit an existing book.
    Requires: bookshelf.can_edit permission
    """
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.publication_year = int(request.POST.get('publication_year'))
        book.save()
        messages.success(request, 'Book updated successfully!')
        return redirect('book_list')
    
    return render(request, 'bookshelf/book_form.html', {
        'book': book,
        'action': 'Edit'
    })

# View to delete a book - requires can_delete permission
@permission_required('bookshelf.can_delete', raise_exception=True)
def book_delete(request, pk):
    """
    Delete a book.
    Requires: bookshelf.can_delete permission
    """
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book_list')
    
    return render(request, 'bookshelf/book_confirm_delete.html', {'book': book})

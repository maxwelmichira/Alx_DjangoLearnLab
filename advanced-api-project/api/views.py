from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Book
from .serializers import BookSerializer

# ListView - Retrieve all books
class BookListView(generics.ListAPIView):
    """
    API view to retrieve list of all books.
    
    - GET /books/ - Returns a list of all books
    - Permissions: Read-only access for all users (authenticated or not)
    - No authentication required for viewing
    
    This view uses Django REST Framework's ListAPIView which provides
    a read-only endpoint for listing all Book instances.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Anyone can read


# DetailView - Retrieve a single book by ID
class BookDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve a single book by its ID.
    
    - GET /books/<int:pk>/ - Returns details of a specific book
    - Permissions: Read-only access for all users
    - No authentication required for viewing
    
    This view uses RetrieveAPIView which provides a read-only endpoint
    for retrieving a single Book instance by its primary key (pk).
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Anyone can read


# CreateView - Add a new book
class BookCreateView(generics.CreateAPIView):
    """
    API view to create a new book.
    
    - POST /books/create/ - Creates a new book
    - Permissions: Only authenticated users can create books
    - Requires authentication token
    
    This view uses CreateAPIView which provides POST method handling
    for creating new Book instances. The view automatically:
    - Validates incoming data using BookSerializer
    - Checks publication_year is not in the future (custom validation)
    - Saves the new book to the database
    - Returns the created book data with 201 status code
    
    Custom Behavior:
    - Inherits all validation from BookSerializer including the
      custom publication_year validation
    - Automatically handles form submission and data validation
    - Returns appropriate error messages if validation fails
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can create


# UpdateView - Modify an existing book
class BookUpdateView(generics.UpdateAPIView):
    """
    API view to update an existing book.
    
    - PUT /books/<int:pk>/update/ - Full update of a book
    - PATCH /books/<int:pk>/update/ - Partial update of a book
    - Permissions: Only authenticated users can update books
    - Requires authentication token
    
    This view uses UpdateAPIView which provides PUT and PATCH methods
    for updating existing Book instances. The view automatically:
    - Retrieves the book by primary key (pk)
    - Validates incoming data using BookSerializer
    - Applies custom validations (e.g., publication_year check)
    - Saves the updated book to the database
    - Returns the updated book data
    
    Custom Behavior:
    - PUT requires all fields to be provided
    - PATCH allows partial updates (only modified fields)
    - All BookSerializer validations are enforced
    - Returns 404 if book with given pk doesn't exist
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can update


# DeleteView - Remove a book
class BookDeleteView(generics.DestroyAPIView):
    """
    API view to delete an existing book.
    
    - DELETE /books/<int:pk>/delete/ - Deletes a book
    - Permissions: Only authenticated users can delete books
    - Requires authentication token
    
    This view uses DestroyAPIView which provides DELETE method
    for removing Book instances. The view automatically:
    - Retrieves the book by primary key (pk)
    - Deletes the book from the database
    - Returns 204 No Content status on success
    - Returns 404 if book with given pk doesn't exist
    
    Custom Behavior:
    - Restricted to authenticated users only
    - No data is returned after successful deletion
    - Cascading deletes are handled by Django ORM based on model relationships
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can delete

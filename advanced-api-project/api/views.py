from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Book
from .serializers import BookSerializer

# ListView - Retrieve all books with filtering, searching, and ordering
class BookListView(generics.ListAPIView):
    """
    API view to retrieve list of all books with advanced query capabilities.
    
    Features:
    - Filtering: Filter books by title, author name, or publication year
    - Searching: Search across title and author name fields
    - Ordering: Sort results by title or publication_year
    
    Query Parameters:
    - Filter examples:
      * ?title=Harry Potter
      * ?author__name=Rowling
      * ?publication_year=1997
    
    - Search examples:
      * ?search=Harry
      * ?search=Rowling
    
    - Ordering examples:
      * ?ordering=title (ascending)
      * ?ordering=-title (descending)
      * ?ordering=publication_year
      * ?ordering=-publication_year
    
    - Combined example:
      * ?search=Harry&ordering=publication_year&author__name=Rowling
    
    Permissions: Read-only access for all users (authenticated or not)
    
    Implementation Details:
    - Uses DjangoFilterBackend for field-specific filtering
    - Uses SearchFilter for text-based searching across multiple fields
    - Uses OrderingFilter for flexible result sorting
    - All filters can be combined in a single request
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Specify fields that can be filtered
    filterset_fields = ['title', 'author__name', 'publication_year']
    
    # Specify fields that can be searched
    search_fields = ['title', 'author__name']
    
    # Specify fields that can be used for ordering
    ordering_fields = ['title', 'publication_year']
    
    # Default ordering
    ordering = ['title']


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
    permission_classes = [IsAuthenticatedOrReadOnly]


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
    permission_classes = [IsAuthenticated]


# UpdateView - Modify an existing book
class BookUpdateView(generics.UpdateAPIView):
    """
    API view to update an existing book.
    
    - PUT /books/update/<int:pk>/ - Full update of a book
    - PATCH /books/update/<int:pk>/ - Partial update of a book
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
    permission_classes = [IsAuthenticated]


# DeleteView - Remove a book
class BookDeleteView(generics.DestroyAPIView):
    """
    API view to delete an existing book.
    
    - DELETE /books/delete/<int:pk>/ - Deletes a book
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
    permission_classes = [IsAuthenticated]

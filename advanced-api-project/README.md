# Advanced API Project - Custom Serializers with Django REST Framework

## Project Overview

This project demonstrates advanced Django REST Framework concepts including custom serializers, nested relationships, and custom validation.

## Models

### Author Model
- **Fields:**
  - `name`: CharField (max 200 characters) - Author's full name
- **Relationships:**
  - One-to-Many with Book model (one author can have multiple books)

### Book Model
- **Fields:**
  - `title`: CharField (max 200 characters) - Book title
  - `publication_year`: IntegerField - Year of publication
  - `author`: ForeignKey to Author model
- **Relationships:**
  - Many-to-One with Author model (many books belong to one author)
  - Uses `related_name='books'` for reverse relationship access

## Serializers

### BookSerializer
- Serializes all fields of the Book model
- **Custom Validation:**
  - `publication_year` cannot be in the future
  - Validates against current year using `datetime.now().year`

### AuthorSerializer
- Includes nested BookSerializer for related books
- **Nested Serialization:**
  - Uses `BookSerializer(many=True, read_only=True)` to serialize all related books
  - Demonstrates one-to-many relationship handling
  - Returns author data with an array of their books

## Relationship Handling

The relationship between Author and Book is handled through:

1. **Database Level:**
   - `Book.author` ForeignKey establishes the relationship
   - `on_delete=models.CASCADE` ensures referential integrity

2. **Serializer Level:**
   - BookSerializer serializes individual books with author reference (ID)
   - AuthorSerializer uses nested BookSerializer to include all related books
   - Django's reverse relationship (`related_name='books'`) allows accessing author.books

## Setup Instructions

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install django djangorestframework
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

## Testing

### Via Django Shell
```python
python manage.py shell

from api.models import Author, Book
from api.serializers import AuthorSerializer, BookSerializer

# Create test data
author = Author.objects.create(name="J.K. Rowling")
book = Book.objects.create(title="Harry Potter", publication_year=1997, author=author)

# Test serializers
book_serializer = BookSerializer(book)
author_serializer = AuthorSerializer(author)

print(book_serializer.data)
print(author_serializer.data)
```

### Via Django Admin
Access the admin panel at `http://127.0.0.1:8000/admin/` to manage authors and books.

## Example Output

### BookSerializer Output:
```json
{
    "id": 1,
    "title": "Harry Potter and the Philosopher's Stone",
    "publication_year": 1997,
    "author": 1
}
```

### AuthorSerializer Output (with nested books):
```json
{
    "id": 1,
    "name": "J.K. Rowling",
    "books": [
        {
            "id": 1,
            "title": "Harry Potter and the Philosopher's Stone",
            "publication_year": 1997,
            "author": 1
        },
        {
            "id": 2,
            "title": "Harry Potter and the Chamber of Secrets",
            "publication_year": 1998,
            "author": 1
        }
    ]
}
```

## Custom Validation Example

Attempting to create a book with a future publication year:
```python
invalid_data = {'title': 'Future Book', 'publication_year': 2027, 'author': 1}
serializer = BookSerializer(data=invalid_data)
serializer.is_valid()  # Returns False
serializer.errors  # {'publication_year': ['Publication year cannot be in the future. Current year is 2026.']}
```

## Author


Max - ALX Django Advanced API Project
## Advanced Query Features

### Filtering

Filter books by specific field values:

**Filter by Title:**
```bash
curl "http://127.0.0.1:8000/api/books/?title=Harry%20Potter"
```

**Filter by Author Name:**
```bash
curl "http://127.0.0.1:8000/api/books/?author__name=Rowling"
```

**Filter by Publication Year:**
```bash
curl "http://127.0.0.1:8000/api/books/?publication_year=1997"
```

**Multiple Filters:**
```bash
curl "http://127.0.0.1:8000/api/books/?author__name=Rowling&publication_year=1997"
```

### Searching

Search across title and author name fields:

**Search for books:**
```bash
curl "http://127.0.0.1:8000/api/books/?search=Harry"
curl "http://127.0.0.1:8000/api/books/?search=Rowling"
```

The search performs case-insensitive matching across both title and author name fields.

### Ordering

Sort results by title or publication year:

**Order by Title (Ascending):**
```bash
curl "http://127.0.0.1:8000/api/books/?ordering=title"
```

**Order by Title (Descending):**
```bash
curl "http://127.0.0.1:8000/api/books/?ordering=-title"
```

**Order by Publication Year (Ascending):**
```bash
curl "http://127.0.0.1:8000/api/books/?ordering=publication_year"
```

**Order by Publication Year (Descending):**
```bash
curl "http://127.0.0.1:8000/api/books/?ordering=-publication_year"
```

### Combined Queries

You can combine filtering, searching, and ordering in a single request:
```bash
# Search for "Harry", filter by author, and sort by year
curl "http://127.0.0.1:8000/api/books/?search=Harry&author__name=Rowling&ordering=publication_year"

# Filter by year and sort by title descending
curl "http://127.0.0.1:8000/api/books/?publication_year=1997&ordering=-title"
```

### Implementation Details

**Filter Backend Configuration:**
- `DjangoFilterBackend`: Enables field-specific filtering
- `SearchFilter`: Enables text search across specified fields
- `OrderingFilter`: Enables result sorting

**BookListView Configuration:**
```python
filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
filterset_fields = ['title', 'author__name', 'publication_year']
search_fields = ['title', 'author__name']
ordering_fields = ['title', 'publication_year']
ordering = ['title']  # Default ordering
```


## API Endpoints

### Public Endpoints (No Authentication Required)

#### List All Books
- **URL:** `GET /api/books/`
- **Description:** Retrieve a list of all books
- **Permissions:** Public (read-only)
- **Response:** 200 OK with array of books
```bash
curl http://127.0.0.1:8000/api/books/
```

#### Get Book Details
- **URL:** `GET /api/books/<int:pk>/`
- **Description:** Retrieve details of a specific book
- **Permissions:** Public (read-only)
- **Response:** 200 OK with book data
```bash
curl http://127.0.0.1:8000/api/books/1/
```

### Protected Endpoints (Authentication Required)

#### Create a Book
- **URL:** `POST /api/books/create/`
- **Description:** Create a new book
- **Permissions:** Authenticated users only
- **Authentication:** Basic or Session authentication required
- **Response:** 201 Created with new book data
```bash
curl -X POST http://127.0.0.1:8000/api/books/create/ \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{"title":"New Book","publication_year":2020,"author":1}'
```

**Validation:**
- `publication_year` cannot be in the future
- Returns 400 Bad Request with error message if validation fails

#### Update a Book
- **URL:** `PUT /api/books/<int:pk>/update/` (full update)
- **URL:** `PATCH /api/books/<int:pk>/update/` (partial update)
- **Description:** Update an existing book
- **Permissions:** Authenticated users only
- **Response:** 200 OK with updated book data
```bash
# Full update (PUT)
curl -X PUT http://127.0.0.1:8000/api/books/1/update/ \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title","publication_year":2021,"author":1}'

# Partial update (PATCH)
curl -X PATCH http://127.0.0.1:8000/api/books/1/update/ \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{"publication_year":2022}'
```

#### Delete a Book
- **URL:** `DELETE /api/books/<int:pk>/delete/`
- **Description:** Delete a book
- **Permissions:** Authenticated users only
- **Response:** 204 No Content on success
```bash
curl -X DELETE http://127.0.0.1:8000/api/books/1/delete/ \
  -u username:password
```

## View Configurations

### Generic Views Used

All views leverage Django REST Framework's generic views for efficient CRUD operations:

1. **BookListView** - `generics.ListAPIView`
   - Provides GET method for listing all books
   - Read-only access for all users

2. **BookDetailView** - `generics.RetrieveAPIView`
   - Provides GET method for single book retrieval
   - Read-only access for all users

3. **BookCreateView** - `generics.CreateAPIView`
   - Provides POST method for creating books
   - Restricted to authenticated users
   - Automatic validation via BookSerializer

4. **BookUpdateView** - `generics.UpdateAPIView`
   - Provides PUT and PATCH methods for updating books
   - Restricted to authenticated users
   - Full and partial updates supported

5. **BookDeleteView** - `generics.DestroyAPIView`
   - Provides DELETE method for removing books
   - Restricted to authenticated users

### Permission Classes

- **IsAuthenticatedOrReadOnly**: Used for ListView and DetailView
  - Allows GET requests from anyone
  - Requires authentication for write operations

- **IsAuthenticated**: Used for CreateView, UpdateView, DeleteView
  - All operations require authentication
  - Unauthenticated requests receive 401 Unauthorized

### Authentication Methods

The API supports two authentication methods:
1. **Basic Authentication**: Username and password in request headers
2. **Session Authentication**: Django session-based authentication (browser)

Configuration in `settings.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}
```

## Testing Examples

### Test Read Access (No Auth)
```bash
# Should succeed
curl http://127.0.0.1:8000/api/books/
curl http://127.0.0.1:8000/api/books/1/
```

### Test Write Access Without Auth
```bash
# Should fail with 401
curl -X POST http://127.0.0.1:8000/api/books/create/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","publication_year":2020,"author":1}'
```

### Test Custom Validation
```bash
# Should fail with validation error (future year)
curl -X POST http://127.0.0.1:8000/api/books/create/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{"title":"Future Book","publication_year":2027,"author":1}'
```

### Test Authenticated Access
```bash
# Should succeed
curl -X POST http://127.0.0.1:8000/api/books/create/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{"title":"Authenticated Book","publication_year":2020,"author":1}'
```

## URL Pattern Structure
```
/api/books/                     - List all books (GET)
/api/books/<int:pk>/            - Get book details (GET)
/api/books/create/              - Create book (POST) - Auth required
/api/books/<int:pk>/update/     - Update book (PUT/PATCH) - Auth required
/api/books/<int:pk>/delete/     - Delete book (DELETE) - Auth required
```

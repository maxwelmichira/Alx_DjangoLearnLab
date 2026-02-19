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

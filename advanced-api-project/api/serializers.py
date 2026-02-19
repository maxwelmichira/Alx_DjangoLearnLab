from rest_framework import serializers
from .models import Author, Book
from datetime import datetime

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Book model.
    
    This serializer handles the serialization and deserialization of Book instances.
    It includes all fields from the Book model and implements custom validation
    to ensure data integrity.
    
    Custom Validation:
        - publication_year: Validates that the publication year is not in the future
    
    Fields:
        - id: Auto-generated primary key (read-only)
        - title: The book's title
        - publication_year: Year the book was published (must not be in the future)
        - author: Foreign key reference to the Author (ID)
    """
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author']
    
    def validate_publication_year(self, value):
        """
        Custom validation method for publication_year field.
        
        Ensures that the publication year is not set to a future date.
        This prevents users from creating books with invalid publication dates.
        
        Args:
            value: The publication_year value to validate
        
        Returns:
            The validated publication_year value
        
        Raises:
            serializers.ValidationError: If publication_year is in the future
        """
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        return value


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Author model with nested Book serialization.
    
    This serializer handles the serialization of Author instances and includes
    a nested representation of all books written by the author. This demonstrates
    handling of one-to-many relationships in DRF serializers.
    
    Nested Serialization:
        - books: Uses BookSerializer to serialize all related books
        - This is a read-only field that dynamically serializes the related books
        - The 'many=True' parameter indicates this is a one-to-many relationship
        - Access to related books is provided through the 'books' related_name
          defined in the Book model's ForeignKey
    
    Fields:
        - id: Auto-generated primary key (read-only)
        - name: The author's full name
        - books: Nested serialization of all books by this author (read-only)
    
    How the relationship is handled:
        1. The Author model doesn't explicitly define a books field
        2. Django automatically creates a reverse relationship via the ForeignKey
           in the Book model with related_name='books'
        3. The AuthorSerializer accesses this reverse relationship to fetch all books
        4. BookSerializer is used to serialize each related book instance
        5. The result is a nested JSON structure with author data containing an array of books
    
    Example JSON output:
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
    """
    # Nested serializer for related books
    # 'many=True' indicates this is a one-to-many relationship
    # 'read_only=True' means this field is only for serialization, not deserialization
    books = BookSerializer(many=True, read_only=True)
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books']

from django.db import models

class Author(models.Model):
    """
    Author model representing a book author.
    
    Fields:
        name: The full name of the author (CharField with max 200 characters)
    
    Relationships:
        - One Author can have many Books (One-to-Many relationship via Book.author foreign key)
    """
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Book model representing a published book.
    
    Fields:
        title: The title of the book (CharField with max 200 characters)
        publication_year: The year the book was published (IntegerField)
        author: Foreign key relationship to Author model
    
    Relationships:
        - Many Books can belong to one Author (Many-to-One relationship)
        - This is established through the ForeignKey field 'author'
        - related_name='books' allows access to all books of an author via author.books.all()
        - on_delete=models.CASCADE ensures that when an author is deleted, all their books are also deleted
    """
    title = models.CharField(max_length=200)
    publication_year = models.IntegerField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    
    def __str__(self):
        return f"{self.title} by {self.author.name}"

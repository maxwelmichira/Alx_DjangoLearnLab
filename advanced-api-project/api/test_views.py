from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Author, Book
from datetime import datetime


class BookAPITestCase(TestCase):
    """
    Comprehensive test suite for Book API endpoints.
    
    Tests cover:
    - CRUD operations (Create, Read, Update, Delete)
    - Authentication and permissions
    - Filtering, searching, and ordering
    - Data validation
    - Status codes and response data integrity
    """
    
    def setUp(self):
        """
        Set up test environment before each test method.
        
        Creates:
        - APIClient for making requests
        - Test user (authenticated)
        - Test author
        - Sample books for testing
        """
        # Create API client
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test author
        self.author = Author.objects.create(name='J.K. Rowling')
        
        # Create sample books
        self.book1 = Book.objects.create(
            title='Harry Potter and the Philosopher\'s Stone',
            publication_year=1997,
            author=self.author
        )
        self.book2 = Book.objects.create(
            title='Harry Potter and the Chamber of Secrets',
            publication_year=1998,
            author=self.author
        )
    
    # ==================== READ OPERATIONS (GET) ====================
    
    def test_list_books_unauthenticated(self):
        """
        Test that unauthenticated users can view book list.
        Expected: 200 OK, returns list of books
        """
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_book_detail_unauthenticated(self):
        """
        Test that unauthenticated users can view book details.
        Expected: 200 OK, returns book data
        """
        response = self.client.get(f'/api/books/{self.book1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
        self.assertEqual(response.data['publication_year'], self.book1.publication_year)
    
    def test_retrieve_nonexistent_book(self):
        """
        Test retrieving a book that doesn't exist.
        Expected: 404 Not Found
        """
        response = self.client.get('/api/books/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ==================== CREATE OPERATIONS (POST) ====================
    
    def test_create_book_authenticated(self):
        """
        Test that authenticated users can create books.
        Expected: 201 Created, book is saved correctly
        """
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'title': '1984',
            'publication_year': 1949,
            'author': self.author.id
        }
        
        response = self.client.post('/api/books/create/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        self.assertEqual(response.data['title'], '1984')
        self.assertEqual(response.data['publication_year'], 1949)
    
    def test_create_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot create books.
        Expected: 403 Forbidden
        """
        data = {
            'title': 'Unauthorized Book',
            'publication_year': 2020,
            'author': self.author.id
        }
        
        response = self.client.post('/api/books/create/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 2)  # No new book created
    
    def test_create_book_future_year_validation(self):
        """
        Test custom validation: publication year cannot be in the future.
        Expected: 400 Bad Request with validation error
        """
        self.client.login(username='testuser', password='testpass123')
        
        future_year = datetime.now().year + 1
        data = {
            'title': 'Future Book',
            'publication_year': future_year,
            'author': self.author.id
        }
        
        response = self.client.post('/api/books/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('publication_year', response.data)
    
    def test_create_book_missing_fields(self):
        """
        Test creating a book with missing required fields.
        Expected: 400 Bad Request
        """
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'title': 'Incomplete Book'
            # Missing publication_year and author
        }
        
        response = self.client.post('/api/books/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # ==================== UPDATE OPERATIONS (PUT/PATCH) ====================
    
    def test_update_book_authenticated(self):
        """
        Test that authenticated users can update books.
        Expected: 200 OK, book is updated correctly
        """
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'title': 'Updated Title',
            'publication_year': 1999,
            'author': self.author.id
        }
        
        response = self.client.put(f'/api/books/update/{self.book1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify database was updated
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated Title')
        self.assertEqual(self.book1.publication_year, 1999)
    
    def test_partial_update_book(self):
        """
        Test partial update (PATCH) of a book.
        Expected: 200 OK, only specified fields are updated
        """
        self.client.login(username='testuser', password='testpass123')
        
        data = {'publication_year': 2000}
        
        response = self.client.patch(f'/api/books/update/{self.book1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify only publication_year was updated
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.publication_year, 2000)
        self.assertEqual(self.book1.title, 'Harry Potter and the Philosopher\'s Stone')
    
    def test_update_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot update books.
        Expected: 403 Forbidden
        """
        data = {
            'title': 'Unauthorized Update',
            'publication_year': 2000,
            'author': self.author.id
        }
        
        response = self.client.put(f'/api/books/update/{self.book1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify book was not updated
        self.book1.refresh_from_db()
        self.assertNotEqual(self.book1.title, 'Unauthorized Update')
    
    # ==================== DELETE OPERATIONS (DELETE) ====================
    
    def test_delete_book_authenticated(self):
        """
        Test that authenticated users can delete books.
        Expected: 204 No Content, book is removed from database
        """
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.delete(f'/api/books/delete/{self.book1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify book was deleted
        self.assertEqual(Book.objects.count(), 1)
        self.assertFalse(Book.objects.filter(id=self.book1.id).exists())
    
    def test_delete_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot delete books.
        Expected: 403 Forbidden
        """
        response = self.client.delete(f'/api/books/delete/{self.book1.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify book still exists
        self.assertEqual(Book.objects.count(), 2)
        self.assertTrue(Book.objects.filter(id=self.book1.id).exists())
    
    def test_delete_nonexistent_book(self):
        """
        Test deleting a book that doesn't exist.
        Expected: 404 Not Found
        """
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.delete('/api/books/delete/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ==================== FILTERING TESTS ====================
    
    def test_filter_books_by_title(self):
        """
        Test filtering books by title.
        Expected: Returns only books matching the title
        """
        response = self.client.get('/api/books/?title=Harry Potter and the Chamber of Secrets')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.book2.title)
    
    def test_filter_books_by_author(self):
        """
        Test filtering books by author name.
        Expected: Returns only books by specified author
        """
        response = self.client.get('/api/books/?author__name=J.K. Rowling')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_filter_books_by_publication_year(self):
        """
        Test filtering books by publication year.
        Expected: Returns only books from specified year
        """
        response = self.client.get('/api/books/?publication_year=1997')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['publication_year'], 1997)
    
    # ==================== SEARCHING TESTS ====================
    
    def test_search_books_by_title(self):
        """
        Test searching books by title keyword.
        Expected: Returns books with matching title
        """
        response = self.client.get('/api/books/?search=Chamber')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn('Chamber', response.data[0]['title'])
    
    def test_search_books_by_author(self):
        """
        Test searching books by author name.
        Expected: Returns books by matching author
        """
        response = self.client.get('/api/books/?search=Rowling')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_search_no_results(self):
        """
        Test searching with no matching results.
        Expected: Returns empty list
        """
        response = self.client.get('/api/books/?search=NonexistentBook')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    # ==================== ORDERING TESTS ====================
    
    def test_order_books_by_title_ascending(self):
        """
        Test ordering books by title in ascending order.
        Expected: Books are sorted alphabetically by title
        """
        response = self.client.get('/api/books/?ordering=title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in response.data]
        self.assertEqual(titles, sorted(titles))
    
    def test_order_books_by_title_descending(self):
        """
        Test ordering books by title in descending order.
        Expected: Books are sorted reverse alphabetically
        """
        response = self.client.get('/api/books/?ordering=-title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in response.data]
        self.assertEqual(titles, sorted(titles, reverse=True))
    
    def test_order_books_by_publication_year(self):
        """
        Test ordering books by publication year.
        Expected: Books are sorted by year
        """
        response = self.client.get('/api/books/?ordering=publication_year')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [book['publication_year'] for book in response.data]
        self.assertEqual(years, sorted(years))
    
    # ==================== COMBINED FUNCTIONALITY TESTS ====================
    
    def test_combined_filter_search_order(self):
        """
        Test combining filtering, searching, and ordering.
        Expected: All query parameters work together correctly
        """
        # Create additional test data
        author2 = Author.objects.create(name='George Orwell')
        Book.objects.create(
            title='1984',
            publication_year=1949,
            author=author2
        )
        
        response = self.client.get('/api/books/?search=Harry&ordering=publication_year')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return Harry Potter books sorted by year
        self.assertGreater(len(response.data), 0)
        years = [book['publication_year'] for book in response.data]
        self.assertEqual(years, sorted(years))

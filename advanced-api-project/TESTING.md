# Testing Documentation - Advanced API Project

## Overview
This document describes the testing strategy, test cases, and how to run tests for the Book API.

## Testing Framework
- **Framework**: Django's built-in test framework (based on Python's unittest)
- **Database**: Separate test database (automatically created and destroyed)
- **Test File**: `api/test_views.py`

## Test Coverage

### CRUD Operations
1. **Create (POST)**
   - Authenticated user can create books
   - Unauthenticated user cannot create books
   - Validation for future publication years
   - Validation for missing required fields

2. **Read (GET)**
   - List all books (unauthenticated access allowed)
   - Retrieve single book details
   - Handle nonexistent book requests (404)

3. **Update (PUT/PATCH)**
   - Full update with PUT (authenticated)
   - Partial update with PATCH (authenticated)
   - Prevent unauthorized updates

4. **Delete (DELETE)**
   - Delete book (authenticated only)
   - Prevent unauthorized deletions
   - Handle nonexistent book deletions

### Advanced Features
1. **Filtering**
   - Filter by title
   - Filter by author name
   - Filter by publication year

2. **Searching**
   - Search by title
   - Search by author name
   - Handle no results

3. **Ordering**
   - Order by title (ascending/descending)
   - Order by publication year (ascending/descending)

4. **Combined Operations**
   - Test multiple query parameters together

### Authentication & Permissions
- Read operations: Public access (no authentication)
- Write operations: Authenticated users only

## Running Tests

### Run All Tests
```bash
python manage.py test api
```

### Run Specific Test Class
```bash
python manage.py test api.test_views.BookAPITestCase
```

### Run Specific Test Method
```bash
python manage.py test api.test_views.BookAPITestCase.test_create_book_authenticated
```

### Run with Verbose Output
```bash
python manage.py test api --verbosity=2
```

### Keep Test Database
```bash
python manage.py test api --keepdb
```

## Test Results Interpretation

### Successful Test Output
```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...........................
----------------------------------------------------------------------
Ran 27 tests in 2.345s

OK
Destroying test database for alias 'default'...
```

### Failed Test Output
```
FAIL: test_create_book_authenticated (api.test_views.BookAPITestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  ...
AssertionError: 201 != 400
```

## Test Database

- Django automatically creates a test database
- Prefix: `test_` + your database name
- Database is destroyed after tests complete
- Use `--keepdb` flag to reuse test database

## Continuous Integration

Add to your CI/CD pipeline:
```bash
python manage.py test api --no-input
```

## Test Best Practices

1. **Isolation**: Each test is independent
2. **setUp Method**: Creates fresh data for each test
3. **Descriptive Names**: Test names explain what they test
4. **Assertions**: Clear expectations with meaningful error messages
5. **Coverage**: Tests cover success and failure scenarios

## Adding New Tests

When adding new features:

1. Write test first (TDD approach)
2. Follow naming convention: `test_<feature>_<scenario>`
3. Include docstring explaining what's being tested
4. Test both success and failure cases
5. Update this documentation

## Test Maintenance

- Run tests before committing code
- Update tests when API changes
- Remove obsolete tests
- Keep tests fast and focused

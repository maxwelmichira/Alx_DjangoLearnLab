# Django Admin Setup for Book Model

1. Registered Book model in `bookshelf/admin.py` using `@admin.register(Book)`.
2. Configured `list_display` to show `title`, `author`, and `publication_year`.
3. Added `search_fields` for `title` and `author`.
4. Added `list_filter` for `publication_year`.
5. Verified in admin interface at http://127.0.0.1:8000/admin/

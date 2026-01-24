# Django Permissions and Groups Setup Guide

## Overview
This document explains how permissions and groups are configured and used in the LibraryProject's bookshelf app.

## Custom Permissions

### Book Model Permissions
The `Book` model has four custom permissions defined in `bookshelf/models.py`:

- **can_view**: Allows users to view the list of books
- **can_create**: Allows users to create new books
- **can_edit**: Allows users to edit existing books
- **can_delete**: Allows users to delete books

These permissions are defined in the `Meta` class of the `Book` model:
```python
class Meta:
    permissions = [
        ("can_view", "Can view book"),
        ("can_create", "Can create book"),
        ("can_edit", "Can edit book"),
        ("can_delete", "Can delete book"),
    ]
```

## Groups Setup

### Recommended Groups
Create the following groups via Django Admin and assign permissions:

1. **Viewers**
   - Permissions: `can_view`
   - Purpose: Users who can only view books

2. **Editors**
   - Permissions: `can_view`, `can_create`, `can_edit`
   - Purpose: Users who can view, create, and edit books but cannot delete

3. **Admins**
   - Permissions: `can_view`, `can_create`, `can_edit`, `can_delete`
   - Purpose: Full access to all book operations

### How to Create Groups (via Django Admin)

1. Run the development server:
   ```bash
   python manage.py runserver
   ```

2. Access Django Admin at `http://127.0.0.1:8000/admin/`

3. Navigate to **Authentication and Authorization** → **Groups**

4. Click **Add Group**

5. Enter group name (e.g., "Viewers")

6. Select the appropriate permissions from the "Available permissions" list:
   - Look for permissions starting with `bookshelf | book | can_`
   - Move selected permissions to "Chosen permissions"

7. Click **Save**

8. Repeat for other groups (Editors, Admins)

## Assigning Users to Groups

### Via Django Admin:
1. Go to **Users** in Django Admin
2. Select a user
3. Scroll to **Groups** section
4. Select the appropriate group(s) from "Available groups"
5. Move to "Chosen groups"
6. Click **Save**

## Permission Enforcement in Views

All views in `bookshelf/views.py` use the `@permission_required` decorator to enforce permissions:

- `book_list`: Requires `bookshelf.can_view`
- `book_create`: Requires `bookshelf.can_create`
- `book_edit`: Requires `bookshelf.can_edit`
- `book_delete`: Requires `bookshelf.can_delete`

Example:
```python
@permission_required('bookshelf.can_edit', raise_exception=True)
def book_edit(request, pk):
    # View logic here
```

The `raise_exception=True` parameter ensures that users without permission receive a 403 Forbidden error.

## Template Permission Checks

Templates also check permissions to show/hide UI elements:

```html
{% if perms.bookshelf.can_create %}
    <a href="{% url 'book_create' %}">Add New Book</a>
{% endif %}
```

This ensures users only see actions they're permitted to perform.

## Testing Permissions

### Steps to Test:

1. **Create test users:**
   ```bash
   python manage.py createsuperuser  # Create admin user first
   ```
   Then create regular users via Django Admin

2. **Create groups and assign permissions** (as described above)

3. **Assign users to different groups:**
   - User A → Viewers group
   - User B → Editors group
   - User C → Admins group

4. **Test access:**
   - Login as User A (Viewer):
     - Should see book list
     - Should NOT see "Add New Book" button
     - Should NOT see Edit/Delete buttons
   
   - Login as User B (Editor):
     - Should see book list
     - Should see "Add New Book" button
     - Should see Edit buttons
     - Should NOT see Delete buttons
   
   - Login as User C (Admin):
     - Should have full access to all operations

5. **Test permission enforcement:**
   - Try accessing URLs directly without permission (e.g., `/bookshelf/books/create/` as a Viewer)
   - Should receive a 403 Forbidden error

## URLs

The bookshelf app provides the following URLs:

- `/bookshelf/books/` - List all books (requires `can_view`)
- `/bookshelf/books/create/` - Create new book (requires `can_create`)
- `/bookshelf/books/<id>/edit/` - Edit book (requires `can_edit`)
- `/bookshelf/books/<id>/delete/` - Delete book (requires `can_delete`)

## Notes

- Superusers bypass all permission checks
- Permissions are enforced at both the view level (decorator) and template level (conditional rendering)
- Users without proper permissions will receive a 403 Forbidden error when attempting unauthorized actions
- Always test with non-superuser accounts to verify permission enforcement

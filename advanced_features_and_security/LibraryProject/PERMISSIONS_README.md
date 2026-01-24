# Permissions and Groups Setup Guide

## Overview
This Django application uses a custom permissions system to control access to Book management features.

## Custom Permissions

### Book Model Permissions
Located in `bookshelf/models.py`, the Book model defines four custom permissions:

- `can_view` - Permission to view books
- `can_create` - Permission to create new books
- `can_edit` - Permission to edit existing books
- `can_delete` - Permission to delete books

## Groups and Permission Assignment

### Recommended Groups Setup

1. **Viewers**
   - Permissions: `can_view`
   - Purpose: Users who can only browse books

2. **Editors**
   - Permissions: `can_view`, `can_create`, `can_edit`
   - Purpose: Users who can create and modify books

3. **Admins**
   - Permissions: `can_view`, `can_create`, `can_edit`, `can_delete`
   - Purpose: Full access to all book management features

## Setting Up Groups (via Django Admin)

1. Navigate to Django Admin: `/admin/`
2. Go to **Authentication and Authorization** > **Groups**
3. Click **Add Group**
4. Create each group and assign permissions:
   - **Viewers**: Select `bookshelf | book | Can view book`
   - **Editors**: Select `can_view`, `can_create`, `can_edit`
   - **Admins**: Select all four permissions

## Views with Permission Enforcement

All views in `bookshelf/views.py` use the `@permission_required` decorator:

- `book_list` - Requires `bookshelf.can_view`
- `book_create` - Requires `bookshelf.can_create`
- `book_edit` - Requires `bookshelf.can_edit`
- `book_delete` - Requires `bookshelf.can_delete`

## Testing Permissions

### Create Test Users

1. Go to Django Admin > Users > Add User
2. Create users: `viewer_user`, `editor_user`, `admin_user`
3. Assign each user to their respective group

### Test Access

1. **As Viewer**:
   - ✅ Can access `/bookshelf/books/` (list view)
   - ❌ Cannot access `/bookshelf/books/create/`
   - ❌ Cannot access edit or delete views

2. **As Editor**:
   - ✅ Can view, create, and edit books
   - ❌ Cannot delete books

3. **As Admin**:
   - ✅ Full access to all operations

## Usage Example
```python
# In views.py
@permission_required('bookshelf.can_edit', raise_exception=True)
def book_edit(request, pk):
    # Only users with can_edit permission can access this view
    book = get_object_or_404(Book, pk=pk)
    # ... rest of the view logic
```

## Security Notes

- All permission checks use `raise_exception=True` to return 403 Forbidden instead of redirecting to login
- Permissions are checked at the view level using decorators
- Groups make it easy to manage permissions for multiple users at once

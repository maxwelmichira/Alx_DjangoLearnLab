"""
Security-focused forms for the bookshelf application.

These forms implement Django's built-in security features:
- CSRF protection (automatic with Django forms)
- Input validation and sanitization
- XSS prevention through auto-escaping
"""

from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    """
    Secure form for creating and editing books.
    
    Security features:
    - Uses Django's ModelForm for automatic validation
    - Prevents SQL injection through ORM
    - Auto-escapes output to prevent XSS
    - Validates data types and field constraints
    """
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book title',
                'maxlength': '200'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter author name',
                'maxlength': '100'
            }),
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter publication year',
                'min': '1000',
                'max': '9999'
            }),
        }
    
    def clean_publication_year(self):
        """
        Validate publication year is within reasonable range.
        Prevents invalid data entry.
        """
        year = self.cleaned_data.get('publication_year')
        if year and (year < 1000 or year > 9999):
            raise forms.ValidationError('Please enter a valid 4-digit year.')
        return year
    
    def clean_title(self):
        """
        Sanitize and validate book title.
        Strips leading/trailing whitespace.
        """
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if not title:
                raise forms.ValidationError('Title cannot be empty or just whitespace.')
        return title


class ExampleForm(forms.Form):
    """
    Example secure form demonstrating Django form security features.
    
    Security features demonstrated:
    - Input validation
    - Type checking
    - Length constraints
    - Required field enforcement
    """
    
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name'
        }),
        help_text='Enter your full name'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        }),
        help_text='We will never share your email'
    )
    
    message = forms.CharField(
        max_length=1000,
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your message',
            'rows': 4
        })
    )
    
    def clean_name(self):
        """Sanitize name input"""
        name = self.cleaned_data.get('name')
        return name.strip() if name else name
    
    def clean_message(self):
        """Sanitize message and check length"""
        message = self.cleaned_data.get('message')
        if message:
            message = message.strip()
            if len(message) < 10:
                raise forms.ValidationError('Message must be at least 10 characters long.')
        return message

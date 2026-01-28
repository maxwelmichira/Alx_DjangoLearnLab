# TimberFlow - Timber Business Management System

A comprehensive Django REST Framework application for managing timber business operations from tree procurement to product sales.

## Project Structure
```
timberflow/
├── users/              # User management and authentication
├── suppliers/          # Supplier management
├── procurement/        # Tree purchasing and procurement
├── processing/         # Production and timber processing
├── inventory/          # Stock and inventory management
├── sales/              # Customer and sales management
├── finance/            # Financial tracking and reporting
├── analytics/          # Business analytics and reports
└── core/               # Shared utilities and base models
```

## Features

- Multi-role user authentication (Admin, Manager, Sales, Inventory)
- Supplier management with performance tracking
- Tree procurement and purchasing
- Processing workflow (trees → finished products)
- Real-time inventory management
- Sales and customer management
- Financial tracking and reporting
- Business analytics and insights

## Technology Stack

- Django 5.x
- Django REST Framework
- Token Authentication
- PostgreSQL (production) / SQLite (development)
- Python 3.12+

## Setup Instructions

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
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

5. Run development server:
```bash
python manage.py runserver
```

## Development Timeline

- Week 1: Foundation & Authentication
- Week 2: Processing & Products
- Week 3: Inventory & Sales
- Week 4: Finance & Analytics
- Week 5: Testing & Documentation

## Author

Max - ALX Django Capstone Project

## License

Educational Project

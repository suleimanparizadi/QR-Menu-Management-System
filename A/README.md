QR Menu Management System

Overview:

Welcome to the QR Menu Management System, a powerful API-based solution designed for restaurants and cafes to manage menus and menu items through QR codes. This project features user authentication, menu creation, item addition, and QR code integration, making it easy to digitalize menu management and enhance user experience.

Features
User Management: Secure sign-up, login, logout, and profile update functionalities with custom user models and authentication.

Menu Management: Create, update, and delete QR menus linked to users.

Menu Item Management: Add, update, remove, and retrieve menu items associated with menus.

QR Code Integration: Generate QR codes for menus and retrieve QR images.

OTP Verification: Secure registration and login using OTP-based authentication.

RESTful API: Fully functional and scalable API endpoints for managing users, menus, and menu items.

Task Processing with Celery: Asynchronous background tasks such as sending OTP codes.

AWS S3 Integration: Cloud storage for menu-related images using AWS S3.

PostgreSQL Database: High-performance database for storing user, menu, and item information.

Extensive Test Coverage: Over 53 tests written to ensure the reliability of views, models, and serializers.


Technologies Used

Backend Framework: Django (v5.1) with Django REST Framework.

Database: PostgreSQL.

Cloud Storage: AWS S3 via the django-storages package.

Task Queue: Celery with RabbitMQ.

Authentication: Token-based authentication and custom phone number-based login. custom authentication based identifier(phone number or username)

Programming Language: Python.

Other Libraries: dotenv (for environment variable management) and various Django and Rest Framework middleware.


Installation
Clone the repository:


API Documentation: Test endpoints using Postman or any other API testing tool.

Admin Panel: Access Django’s admin panel at /admin for managing data (e.g., users, menus, items).

Menu QR Code: Generate QR codes for menus using the API and retrieve them for printing or scanning.

Testing
The project includes comprehensive testing to ensure its reliability:


53 Tests Covering:

Views: Testing endpoint behaviors.

Models: Validating database functionality.

Serializers: Ensuring accurate data serialization and validation.


Contribution
Feel free to fork this repository and contribute by submitting pull requests. All contributions are welcome!
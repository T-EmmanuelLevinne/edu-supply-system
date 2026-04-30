# School Supply E-Commerce

A comprehensive Django-based e-commerce platform for school supplies. Built with Django 6 and Bootstrap 5.

## Features
- **3 Django Apps**: `products`, `customers`, and `orders`.
- **User Roles**: Client (Customer), Staff, Admin.
- **Client Sign Up**: Custom user registration linked to a Customer profile.
- **Clean UI**: Premium design inspired by modern e-commerce trends, using Bootstrap 5.
- **CRUD Operations**: Complete Create, Read, Update, Delete flows for products, profiles, and orders.

## Setup Instructions

1. **Clone or Download the repository.**
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment:**
   ```bash
   # Windows
   .\venv\Scripts\activate
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```
6. **Create a superuser (Admin/Staff):**
   ```bash
   python manage.py createsuperuser
   ```
7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
8. **Access the application:** Open your browser and navigate to `http://127.0.0.1:8000/`.

## App Structure
1. **Core Entity (`products`)**: Manages the inventory of school supplies.
2. **Secondary Entity (`customers`)**: Manages client accounts and shipping profiles.
3. **Transaction (`orders`)**: Links customers to products they purchase.

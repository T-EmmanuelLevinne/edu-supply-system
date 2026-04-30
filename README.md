# EduSupply Store

A comprehensive web-based e-commerce platform built with Django for managing the purchase and delivery of school supplies.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [User Roles](#user-roles)
- [Application Modules](#application-modules)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Support](#support)

## Overview
EduSupply Store is a Django-based web application designed to streamline the procurement of educational materials for students. It provides a complete e-commerce experience including dynamic product catalogs, a responsive shopping cart, order tracking, and a dedicated portal for store staff and delivery personnel.

## Features

### Core Features
- Secure user authentication (Username or Email login)
- Interactive password visibility toggles
- Role-based access control (Student, Staff, Delivery Personnel, Admin)
- Clean, responsive UI built with Bootstrap 5

### Shopping & Customer Experience
- Dynamic product catalog with categories (Notebooks, Bags, Art Supplies, etc.)
- Real-time typeahead search functionality
- AJAX-powered "Hover Cart" for seamless add/remove actions
- One-click Wishlist system for saving products
- Comprehensive order history and status tracking

### Delivery & Logistics
- Dedicated Delivery Dashboard for staff personnel
- Real-time updates for order statuses (Processing, Out for Delivery, Delivered)
- Receipt scanning and verification interface during handoff

### Administration & Store Management
- Comprehensive dashboard overview of sales and inventory
- Complete student directory management
- Order processing and management (Accept, Cancel, Update)
- Full CRUD operations for products, categories, and users

## System Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.10 or higher |
| Django | 6.0.4 |
| Database | SQLite (default) |
| Browser | Chrome, Firefox, Edge, Safari |

**Recommended:**
- 4GB RAM minimum
- 1GB free disk space

## Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd schoolsupply
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser account**
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

### Development Server

1. Activate your virtual environment
2. Run the development server:
   ```bash
   python manage.py runserver
   ```
3. Open your browser and navigate to: `http://127.0.0.1:8000/`

### Admin Panel
Access the Django admin panel at: `http://127.0.0.1:8000/admin/`

## User Roles

| Role | Permissions |
|------|-------------|
| **Student** | Browse products, manage cart and wishlist, place orders, view order history, update personal profile. |
| **Delivery Staff** | Access delivery dashboard, scan receipts, update order delivery statuses. |
| **Store Staff** | Monitor incoming orders, handle order cancellations, view student directory. |
| **Admin** | Full system access, product inventory management, user administration, system configuration. |

## Application Modules

### Core & Configuration (`school_supply_store/`)
- Main Django settings and routing
- Custom authentication backends (Email/Username login)

### Products (`/products/`)
- Product catalog and inventory
- Category management
- Dynamic search APIs
- Wishlist management

### Customers (`/customers/`)
- User profile management
- Registration and dual-login handlers
- Student directory views

### Orders (`/orders/`)
- Shopping cart processing
- Checkout logic
- Order history and tracking
- Delivery dashboard and receipt scanning

## Project Structure

```text
schoolsupply/
├── school_supply_store/  # Main Django settings & configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── products/             # Inventory, Search & Wishlist
├── customers/            # User Profiles & Authentication
├── orders/               # Cart, Checkout & Delivery
├── templates/            # Global HTML templates (base.html, etc.)
├── static/               # Global static files (CSS, JS, Images)
├── media/                # User uploaded files (Product images)
├── manage.py
├── requirements.txt
└── db.sqlite3            # SQLite database
```

## Configuration

**Key Settings (`school_supply_store/settings.py`)**

| Setting | Description |
|---------|-------------|
| `DEBUG` | Set to `False` in production |
| `ALLOWED_HOSTS` | Configure for production domain |
| `DATABASE` | SQLite by default |
| `AUTHENTICATION_BACKENDS` | Custom configured for Email & Username login |

## Support

**Group Members / Developers:**
- Emmanuel Levinne Tecson - UI & UX Designer
- Neil Brian Molarte - Front-end Developer
- Asiong Jared - Backend Developer
- Jared Lita Ponteveros - Full-stack Developer

### Version History
**Version 1.0 - Initial Release**
- Core product catalog and shopping cart
- AJAX-powered UI interactions
- Dual-login authentication system
- Delivery and Admin dashboards

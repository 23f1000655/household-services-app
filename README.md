# Household Services Application

A multi-user web application built with Flask that connects customers with verified service professionals for home servicing needs. The platform supports three distinct roles: **Admin**, **Service Professional**, and **Customer**.

---

## Features

### Admin
- Approve or reject service professional registrations
- Add, edit, and delete service categories
- View all active service requests across the platform
- Access summary charts (bar and pie) for platform activity

### Service Professional
- Register and set up a profile with service specialisation
- Accept or reject incoming service requests from customers
- Track request history and completion status

### Customer
- Register and log in to browse available services
- Create and manage service requests
- Search for professionals by service type or location
- Close completed requests and view history

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python) |
| Database ORM | SQLAlchemy |
| Templating | Jinja2 |
| Authentication | Werkzeug Security (password hashing) |
| Charts | Matplotlib (rendered via base64 + IO) |
| Frontend | HTML, CSS |
| File Handling | Werkzeug Utils |

---

## Database Schema (ER Overview)

- **Customer** makes `ServiceRequest` and has an `Address`
- **Professional** handles `ServiceRequest` and offers `Service`
- **Admin** manages `Service` categories
- **ServiceRequest** links Customer and Professional through a requested Service

---

## Project Structure

```
project/
├── app.py               # Main application, all routes
├── models.py            # SQLAlchemy models
├── templates/
│   ├── admin/           # Admin dashboard pages
│   ├── professional/    # Professional dashboard pages
│   └── customer/        # Customer dashboard pages
├── static/
│   └── css/             # Stylesheets
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.8 or above
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/household-services-app.git
cd household-services-app

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
python app.py
```

Open your browser and go to `http://127.0.0.1:5000`

### Default Admin Login

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin@098` |

> These are demo credentials for testing and evaluation purposes only.

---

## Requirements

```
Flask
Flask-SQLAlchemy
Werkzeug
Matplotlib
```

Generate the full list with:
```bash
pip freeze > requirements.txt
```

---

## Course Context

This project was built as part of the **MAD 1 (Modern Application Development 1)** course at **IIT Madras BS in Data Science and Applications**.

---

## License

This project is for academic purposes. Not licensed for commercial use.

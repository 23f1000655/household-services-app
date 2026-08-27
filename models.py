from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Customer Model
class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.Integer, nullable=False)

# Professional Model
class Professional(db.Model):
    professional_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    service_name = db.Column(db.String, db.ForeignKey('service.service_name'), nullable=False)
    experience = db.Column(db.Integer, nullable = False)
    document = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    approved = db.Column(db.Boolean, nullable=False, default=False)
    service_requests = db.relationship('ServiceRequest', backref='professional', lazy=True)
    service = db.relationship('Service', backref='professionals', lazy=True)

# Service Model
class Service(db.Model):
    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=True)

# Admin Model
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Service Request Model
class ServiceRequest(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    customer_username = db.Column(db.Integer, db.ForeignKey('customer.username'), nullable=False)  # Customer making the request
    service_name = db.Column(db.Integer, db.ForeignKey('service.service_name'), nullable=False)  # Service requested
    requested_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Requested')  # Requested, Accepted, or Closed
    assigned_professional_id = db.Column(db.Integer, db.ForeignKey('professional.professional_id'), nullable=True)  # Assigned professional
    rating = db.Column(db.Integer, nullable=True)
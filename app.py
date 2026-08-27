from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sqlalchemy.sql import func
from datetime import *
from models import *
import os
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Ensure required folders exist on the server
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

# Utility to check allowed files
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user is a customer
        customer = Customer.query.filter_by(username=username).first()
        if customer and check_password_hash(customer.password, password):
            return redirect(url_for('customer_dashboard', username=customer.username))
        
        # Check if the user is a professional
        professional = Professional.query.filter_by(username=username).first()
        if professional and check_password_hash(professional.password, password):
            return redirect(url_for('professional_dashboard', username=professional.username))

        return redirect(url_for('error_login'))

    return render_template('login.html')


@app.route('/cust_register', methods=['GET', 'POST'])
def cust_register():
    if request.method == 'POST':
        username = request.form['username']

        # Check if username already exists
        existing_customer = Customer.query.filter_by(username=username).first()
        if existing_customer:
            return redirect(url_for('username_exists'))
        
        existing_professional = Professional.query.filter_by(username=username).first()
        if existing_professional:
            return redirect(url_for('username_exists'))
        
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            return redirect(url_for('username_exists'))

        # Create a new customer
        new_customer = Customer(
            full_name=request.form['full_name'],
            username=username,
            password=generate_password_hash(request.form['password']),
            phone_number=request.form['phone_number'],
            address=request.form['address'],
            pincode=request.form['pincode']
        )
        db.session.add(new_customer)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('cust_register.html')

@app.route('/sp_register', methods=['GET', 'POST'])
def sp_register():
    if request.method == 'POST':
        username = request.form['username']

        # Check if username already exists
        existing_customer = Customer.query.filter_by(username=username).first()
        if existing_customer:
            return redirect(url_for('username_exists'))
        
        existing_professional = Professional.query.filter_by(username=username).first()
        if existing_professional:
            return redirect(url_for('username_exists'))
        
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            return redirect(url_for('username_exists'))

        service_name = request.form['service_name']
        service = Service.query.filter_by(service_name=service_name).first()

        # Handle document upload
        file = request.files['documents']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            return redirect(url_for('invalid_file'))

        # Create a new professional
        new_professional = Professional(
            full_name=request.form['full_name'],
            username=username,
            password=generate_password_hash(request.form['password']),
            phone_number=request.form['phone_number'],
            experience=request.form['experience'],
            address=request.form['address'],
            pincode=request.form['pincode'],
            service_name=service.service_name,
            document=filename
        )
        db.session.add(new_professional)
        db.session.commit()

        return redirect(url_for('login'))

    services = Service.query.all()
    return render_template('sp_register.html', services=services)


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the Admin table for the admin user
        admin = Admin.query.filter_by(username=username).first()

        # Check if admin exists and password matches
        if admin and password == 'admin@098':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('error_login'))

    return render_template('admin-login.html')

@app.route('/error_login')
def error_login():
    return render_template('error_login.html')

@app.route('/username_exists')
def username_exists():
    return render_template('username_exists.html')

@app.route('/invalid_file')
def invalid_file():
    return render_template('invalid_file.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    # Retrieve data from the database
    services = Service.query.all()
    professionals = Professional.query.all()
    service_requests = ServiceRequest.query.all()

    # Pass the data to the template
    return render_template(
        'admin_dashboard.html',  # Name of your dashboard HTML file
        services=services,
        professionals=professionals,
        service_requests=service_requests
    )

@app.route('/view_service/<int:service_id>')
def view_service(service_id):
    service = Service.query.get_or_404(service_id)
    return render_template('view_service.html', service=service)

@app.route('/edit_service/<int:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    if request.method == 'POST':
        new_price = request.form['base_price']
        service.base_price = float(new_price)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_service.html', service=service)

@app.route('/delete_service/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/new_service', methods=['GET', 'POST'])
def new_service():
    if request.method == 'POST':
        service_name = request.form['service_name']
        base_price = float(request.form['base_price']) if request.form['base_price'] else None

        new_service = Service(
            service_name=service_name,
            base_price=base_price
        )
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('new_service.html')

@app.route('/approve_professional/<int:professional_id>', methods=['POST'])
def approve_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    if professional:
        professional.approved = True
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_professional/<int:professional_id>', methods=['POST'])
def reject_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    if professional:
        professional.approved = False
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/professional_details/<int:professional_id>')
def view_professional_details(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    return render_template('professional_details.html', professional=professional)

UPLOADED_FOLDER = os.path.join(os.getcwd(), 'uploads')
@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(UPLOADED_FOLDER, filename)

@app.route('/admin_search', methods=['GET', 'POST'])
def admin_search():
    if request.method == 'POST':
        table = request.form['table']
        query = request.form['query']
        rows = []
        columns = []

        if table == 'customers':
            rows = Customer.query.filter(Customer.username.like(f"%{query}%")).all()
            columns = ['ID', 'Name', 'Username', 'Phone', 'Address']
            rows = [{
                "ID": row.customer_id,
                "Name": row.full_name,
                "Username": row.username,
                "Phone": row.phone_number,
                "Address": row.address
            } for row in rows]
        
        elif table == 'professionals':
            rows = Professional.query.filter(Professional.username.like(f"%{query}%")).all()
            columns = ['ID', 'Name', 'Experience', 'Biodata', 'Service Name', 'Approved']
            rows = [{
                "ID": row.professional_id,
                "Name": row.full_name,
                "Experience": row.experience,
                "Biodata": row.document,
                "Service Name": row.service_name,
                "Approved" : row.approved
            } for row in rows]

        elif table == 'services':
            rows = Service.query.filter(Service.service_name.like(f"%{query}%")).all()
            columns = ['Service ID', 'Service Name', 'Base Price']
            rows = [{
                "Service ID": row.service_id,
                "Service Name": row.service_name,
                "Base Price": row.base_price
            } for row in rows]

        return render_template('admin_search.html', rows=rows, columns=columns)

    return render_template('admin_search.html', rows=None, columns=[])

@app.route('/admin_summary')
def admin_summary():
    # Fetching ratings summary
    ratings_data = db.session.query(
        ServiceRequest.rating, func.count(ServiceRequest.rating)
    ).group_by(ServiceRequest.rating).all()

    ratings_summary = {}
    for rating, count in ratings_data:
        if rating:
            ratings_summary[f"{int(rating)} Star"] = count

    # Fetching service requests summary
    requests_data = db.session.query(
        ServiceRequest.status, func.count(ServiceRequest.status)
    ).group_by(ServiceRequest.status).all()

    requests_summary = {}
    for status, count in requests_data:
        requests_summary[status.capitalize()] = count

    # Generate charts
    generate_pie_chart(ratings_summary, 'static/ratings_chart.png', 'Customer Ratings')
    generate_bar_chart(requests_summary, 'static/requests_chart.png', 'Service Requests')

    # Render the template
    return render_template('admin_summary.html')
def generate_pie_chart(data, filepath, title):
    labels = data.keys()
    sizes = data.values()
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title(title)
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()

def generate_bar_chart(data, filepath, title):
    labels = list(data.keys())
    values = list(data.values())
    plt.figure(figsize=(8, 6))
    plt.bar(labels, values, color=['#ff9999', '#66b3ff', '#99ff99'])
    plt.title(title)
    plt.ylabel('Count')
    plt.xlabel('Status')
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()

@app.route('/professional_dashboard/<username>', methods=['GET'])
def professional_dashboard(username):
    # Fetch the logged-in professional using the session
    professional = Professional.query.filter_by(username=username).first()

    # Check if the professional is approved
    if not professional.approved:
        return render_template('professional_dashboard.html', professional=professional, today_services=[], closed_services=[])

    # Fetch today's service requests assigned to the professional
    today_services = ServiceRequest.query.filter(
        ServiceRequest.assigned_professional_id == professional.professional_id,
        ServiceRequest.status == 'Requested'
    ).join(Customer).add_columns(
        ServiceRequest.request_id,
        ServiceRequest.assigned_professional_id,
        Customer.full_name,
        Customer.phone_number,
        Customer.address,
        Customer.pincode,
        ServiceRequest.status
    ).all()

    # Fetch closed service requests assigned to the professional
    closed_services = ServiceRequest.query.filter(
        ServiceRequest.assigned_professional_id == professional.professional_id,
        ServiceRequest.status == 'Closed'
    ).join(Customer).add_columns(
        ServiceRequest.request_id,
        ServiceRequest.assigned_professional_id,
        Customer.full_name,
        Customer.phone_number,
        Customer.address,
        Customer.pincode,
        ServiceRequest.requested_date,
        ServiceRequest.rating
    ).all()

    print(today_services)
    return render_template(
        'professional_dashboard.html',
        professional=professional,
        today_services=today_services,
        closed_services=closed_services
    )

@app.route('/accept_service/<int:request_id>/<int:professional_id>', methods=['POST'])
def accept_service(request_id, professional_id):
    # Fetch the service request
    service_request = ServiceRequest.query.get_or_404(request_id)

    # Fetch the professional by username
    professional = Professional.query.filter_by(professional_id=professional_id).first()

    # If professional is not found or doesn't match the assigned professional, abort
    if not professional or service_request.assigned_professional_id != professional.professional_id:
        abort(403)

    # Update the service request status
    service_request.status = 'Accepted'
    db.session.commit()

    return redirect(url_for('professional_dashboard', username=professional.username))

@app.route('/professional_search/<username>', methods=['GET', 'POST'])
def professional_search(username):
    # Fetch the professional based on the username
    professional = Professional.query.filter_by(username=username).first()
    if not professional:
        abort(404)  # Handle case where the username is invalid

    # Define columns for the search dropdown
    columns = ['Request ID', 'Customer UserName', 'Service Name', 'Requested Date', 'Status', 'Rating']
    rows = None  # Placeholder for search results

    if request.method == 'POST':
        # Get the selected column and the query entered by the professional
        column = request.form.get('table')
        query = request.form.get('query')

        # Map column names to database fields and filter results for the logged-in professional
        if column == 'Request ID':
            rows = ServiceRequest.query.filter(
                ServiceRequest.request_id == query,
                ServiceRequest.assigned_professional_id == professional.professional_id
            ).all()
        elif column == 'Customer UserName':
            rows = ServiceRequest.query.filter(
                ServiceRequest.customer_username.ilike(f'%{query}%'),
                ServiceRequest.assigned_professional_id == professional.professional_id
            ).all()
        elif column == 'Service Name':
            rows = ServiceRequest.query.filter(
                ServiceRequest.service_name.ilike(f'%{query}%'),
                ServiceRequest.assigned_professional_id == professional.professional_id
            ).all()
        elif column == 'Requested Date':
            rows = ServiceRequest.query.filter(
                ServiceRequest.requested_date.like(f'%{query}%'),
                ServiceRequest.assigned_professional_id == professional.professional_id
            ).all()
        elif column == 'Status':
            rows = ServiceRequest.query.filter(
                ServiceRequest.status.ilike(f'%{query}%'),
                ServiceRequest.assigned_professional_id == professional.professional_id
            ).all()
        elif column == 'Rating':
            rows = ServiceRequest.query.filter(
                ServiceRequest.rating == query,
                ServiceRequest.assigned_professional_id == professional.professional_id
            ).all()

    return render_template(
        'professional_search.html',
        rows=rows,
        columns=columns,
        professional=professional
    )

@app.route('/professional_summary/<username>')
def professional_summary(username):
    professional = Professional.query.filter_by(username=username).first()
    if not professional:
        abort(404)

    # Fetch ratings for this professional
    ratings = ServiceRequest.query.filter_by(assigned_professional_id=professional.professional_id).all()
    rating_counts = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
    for request in ratings:
    # Ensure rating is valid and within expected range
        if request.rating is not None and request.rating in [1, 2, 3, 4, 5]:
            rating_counts[str(request.rating)] += 1

    # Generate pie chart for ratings
    plt.figure(figsize=(6,6))
    # Filter out zero values for plotting
    filtered_counts = {key: value for key, value in rating_counts.items() if value > 0}

    if filtered_counts:  # Only plot if there are non-zero values
        plt.pie(filtered_counts.values(), labels=filtered_counts.keys(), autopct='%1.1f%%', startangle=90, colors=['#3a2234', '#6a1b4d', '#c1547e', '#f4d1dc', '#5C6BC0'])
    else:
        plt.text(0.5, 0.5, 'No Ratings Available', ha='center', va='center')
    plt.title('Customer Ratings Distribution')
    pie_img = io.BytesIO()
    plt.savefig(pie_img, format='png')
    pie_img.seek(0)
    pie_img_base64 = base64.b64encode(pie_img.getvalue()).decode('utf8')
    pie_img_url = 'data:image/png;base64,' + pie_img_base64

    # Fetch requests and their statuses
    requests = ServiceRequest.query.filter_by(assigned_professional_id=professional.professional_id).all()
    status_counts = {'Received': 0, 'Closed': 0, 'Rejected': 0}
    for request in requests:
        if request.status in status_counts:  # Ensure the status is valid
            status_counts[request.status] += 1

    # Generate bar chart for service requests status
    plt.figure(figsize=(8,6))
    plt.bar(status_counts.keys(), status_counts.values(), color='#5C6BC0')
    plt.xlabel('Request Status')
    plt.ylabel('Number of Requests')
    plt.title('Service Requests Summary by Status')
    bar_img = io.BytesIO()
    plt.savefig(bar_img, format='png')
    bar_img.seek(0)
    bar_img_base64 = base64.b64encode(bar_img.getvalue()).decode('utf8')
    bar_img_url = 'data:image/png;base64,' + bar_img_base64

    return render_template('professional_summary.html',professional=professional, ratings_chart=pie_img_url, requests_chart=bar_img_url)

@app.route('/customer_dashboard/<username>', methods=['GET'])
def customer_dashboard(username):
    customer = Customer.query.filter_by(username=username).first()
    services = Service.query.all()
    service_history = ServiceRequest.query.filter_by(customer_username=username).all()

    return render_template(
        'customer_dashboard.html',
        customer=customer,
        services=services,
        service_history=service_history
    )

@app.route('/service_professionals/<service_name>/<username>', methods=['GET'])
def service_professionals(service_name,username):
    customer = Customer.query.filter_by(username=username).first()
    professionals = Professional.query.filter_by(service_name=service_name, approved=True).all()
    return render_template(
        'service_professionals.html',
        service_name=service_name,
        customer=customer,
        professionals=professionals,
        Service=Service
    )

@app.route('/book_service/<int:professional_id>/<service_name>/<username>', methods=['POST'])
def book_service(professional_id, service_name, username):
    customer = Customer.query.filter_by(username=username).first()
    professional = Professional.query.filter_by(professional_id=professional_id).first()

    if not professional:
        return redirect(url_for('customer_dashboard', username=username))

    # Create a new service request
    new_request = ServiceRequest(
        customer_username=customer.username,
        service_name=service_name,
        requested_date=date.today(),
        status='Requested',
        assigned_professional_id=professional.professional_id
    )

    db.session.add(new_request)
    db.session.commit()

    return redirect(url_for('customer_dashboard', username=username))

@app.route('/close_service/<int:request_id>/<username>', methods=['GET', 'POST'])
def close_service(request_id, username):
    customer = Customer.query.filter_by(username=username).first()
    service_request = ServiceRequest.query.get_or_404(request_id)

    if request.method == 'POST':
        # Fetch the rating from the form
        rating = int(request.form.get('rating'))

        # Update the service request status and rating
        service_request.status = 'Closed'
        service_request.rating = rating
        db.session.commit()

        # Update the professional's rating (calculate average)
        professional = service_request.professional
        if professional.service_requests:
            ratings = [req.rating for req in professional.service_requests if req.rating]
            professional.rating = sum(ratings) // len(ratings)
            db.session.commit()

        # Redirect to the customer dashboard
        return redirect(url_for('customer_dashboard', username=username))

    return render_template('close_service.html', service_request=service_request, customer=customer)

@app.route('/customer_search/<username>', methods=['GET', 'POST'])
def customer_search(username):
    customer = Customer.query.filter_by(username=username).first_or_404()
    services = Service.query.all()  # Fetch all services
    rows = []

    if request.method == 'POST':
        service_name = request.form.get('service')
        query = request.form.get('query')

        if query:
            rows = Professional.query.filter(
                Professional.service_name == service_name,
                Professional.full_name.ilike(f'%{query}%'),
                Professional.approved == True
            ).all()
        else:
            rows = Professional.query.filter(
                Professional.service_name == service_name,
                Professional.approved == True
            ).all()

    return render_template(
        'customer_search.html',
        customer=customer,
        services=services,
        rows=rows,
        Service=Service
    )

@app.route('/customer_summary/<username>')
def customer_summary(username):
    # Get the logged-in customer's ID
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        abort(404)

    # Fetch requests raised by this customer
    requests = ServiceRequest.query.filter_by(customer_username=username).all()
    status_counts = {'Requested': 0, 'Closed': 0, 'Accepted': 0}
    
    for request in requests:
        if request.status == 'Requested':
            status_counts['Requested'] += 1
        elif request.status == 'Closed':
            status_counts['Closed'] += 1
        elif request.status == 'Accepted':
            status_counts['Accepted'] += 1

    # Generate bar chart for service requests status
    plt.figure(figsize=(8,6))
    plt.bar(status_counts.keys(), status_counts.values(), color='#5C6BC0')
    plt.xlabel('Request Status')
    plt.ylabel('Number of Requests')
    plt.title('Customer Service Requests Summary by Status')
    
    # Save chart to memory
    bar_img = io.BytesIO()
    plt.savefig(bar_img, format='png')
    bar_img.seek(0)
    bar_img_base64 = base64.b64encode(bar_img.getvalue()).decode('utf8')
    bar_img_url = 'data:image/png;base64,' + bar_img_base64

    return render_template('customer_summary.html',customer=customer, requests_chart=bar_img_url)

with app.app_context():
    db.create_all()
    
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', password='admin@098')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
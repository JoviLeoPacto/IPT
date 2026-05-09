from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-super-secret-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and password.')
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/customer')
def customer_page():
    customers = Customer.query.all()
    customers_list = [{"id": c.id, "name": c.name, "email": c.email, "phone": c.phone} for c in customers]
    return jsonify(customers_list)

@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    customers_list = [{"id": c.id, "name": c.name, "email": c.email, "phone": c.phone} for c in customers]
    return jsonify(customers_list), 200

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if customer:
        return jsonify({"id": customer.id, "name": customer.name, "email": customer.email, "phone": customer.phone}), 200
    return jsonify({"error": "Customer not found"}), 404

@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({"error": "Name and email are required"}), 400
    
    new_customer = Customer(name=data['name'], email=data['email'], phone=data.get('phone', ''))
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "Customer created successfully", "id": new_customer.id}), 201

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    if 'name' in data:
        customer.name = data['name']
    if 'email' in data:
        customer.email = data['email']
    if 'phone' in data:
        customer.phone = data['phone']
        
    db.session.commit()
    return jsonify({"message": "Customer updated successfully"}), 200

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
        
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        user = User.query.filter_by(username='jovi').first()
        if not user:
            hashed_pw = generate_password_hash('12345', method='scrypt')
            new_user = User(username='jovi', password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            print("User 'jovi' created successfully!")
            
        if Customer.query.count() < 20:
            for i in range(Customer.query.count(), 20):
                dummy_customer = Customer(
                    name=f'Customer {i+1}', 
                    email=f'customer{i+1}@example.com',
                    phone=f'555-01{str(i).zfill(2)}'
                )
                db.session.add(dummy_customer)
            db.session.commit()
            print(f"Added customers. The database now has {Customer.query.count()} customers.")
            
    app.run(debug=True)

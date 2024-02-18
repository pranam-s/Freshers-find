from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import InputRequired, Length, Email
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = r'ajo3o10c9vmnem2p109e90*382901@wji19*!2.djd98a0erqpoivmzxv,.vb/erqw;erq1q]['
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////test.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(15))
    collegeid = db.Column(db.String(12), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    negotiable = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image = db.Column(db.LargeBinary)


@app.route('/item', methods=['POST'])
@login_required
def add_item():
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    negotiable = 'negotiable' in request.form
    if 'image' not in request.files:
        return jsonify({'message': 'No image provided'}), 400
    image = request.files['image'].read()
    new_item = Item(name=name, description=description, price=price, negotiable=negotiable, user_id=current_user.id, image=image)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'New item created'}), 201

@app.route('/item/<item_id>/image', methods=['GET'])
def get_item_image(item_id):
    item = Item.query.filter_by(id=item_id).first()
    if not item:
        return jsonify({'message': 'No item found'}), 404
    return send_file(io.BytesIO(item.image), mimetype='image/jpeg')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/item/<item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.filter_by(id=item_id).first()
    if not item:
        return jsonify({'message': 'No item found'}), 404
    return jsonify({'name': item.name, 'description': item.description, 'price': item.price, 'negotiable': item.negotiable}), 200

@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({'message': 'You are logged in'}), 200
    email = request.form.get('email')
    password = request.form.get('password')
    remember = 'remember' in request.form
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user, remember=remember)
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/is_logged_in', methods=['GET'])
def is_logged_in():
    if current_user.is_authenticated:
        return jsonify({'message': 'User is logged in'}), 200
    else:
        return jsonify({'message': 'User is not logged in'}), 401

@app.route('/signup', methods=['POST'])
def signup():
    if current_user.is_authenticated:
        return jsonify({'message': 'You are logged in'}), 200
    fullname = request.form.get('fullname')
    collegeid = request.form.get('collegeid')
    email = request.form.get('email')
    password = request.form.get('password')
    hashed_password = generate_password_hash(password)
    new_user = User(fullname=fullname, collegeid=collegeid, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registered successfully'}), 201

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

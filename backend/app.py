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
    username = db.Column(db.String(15), unique=True)
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

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

class ItemForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(max=100)])
    description = StringField('description', validators=[InputRequired(), Length(max=500)])
    cost = IntegerField('cost', validators=[InputRequired()])

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
    username = request.form.get('username')
    password = request.form.get('password')
    remember = 'remember' in request.form
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user, remember=remember)
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registered successfully'}), 201

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = ItemForm()
    if form.validate_on_submit():
        new_item = Item(name=form.name.data, description=form.description.data, cost=form.cost.data, user_id=current_user.id)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

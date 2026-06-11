import os
import json
from datetime import datetime

import numpy as np
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'carprice.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please sign in to access the valuation tool.'
login_manager.login_message_category = 'info'


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    predictions = db.relationship('Prediction', backref='user', lazy=True,
                                   cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company = db.Column(db.String(80), nullable=False)
    car_model = db.Column(db.String(150), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    kms_driven = db.Column(db.Integer, nullable=False)
    fuel_type = db.Column(db.String(20), nullable=False)
    predicted_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------------------
# Load ML model weights + lookup data
#
# The original notebook saved a scikit-learn Pipeline (OneHotEncoder +
# LinearRegression) as a pickle. Pickled sklearn objects are tied to the
# exact scikit-learn version they were created with, which causes
# "AttributeError: ... has no attribute '_RemainderColsList'" (or similar)
# errors when loaded with a different version.
#
# To avoid that entirely, the trained OneHotEncoder categories and the
# LinearRegression coefficients/intercept were extracted once and saved as
# plain JSON (model/model_weights.json). Prediction is then just a
# one-hot encode + dot product, done with numpy only - no scikit-learn
# dependency or version coupling at runtime.
# ---------------------------------------------------------------------------
with open(os.path.join(BASE_DIR, 'model', 'model_weights.json')) as f:
    WEIGHTS = json.load(f)

NAME_CATEGORIES = WEIGHTS['name_categories']
COMPANY_CATEGORIES = WEIGHTS['company_categories']
FUEL_CATEGORIES = WEIGHTS['fuel_categories']  # includes the literal string 'nan'
COEF = np.array(WEIGHTS['coef'])
INTERCEPT = WEIGHTS['intercept']

with open(os.path.join(BASE_DIR, 'model', 'company_models.json')) as f:
    COMPANY_MODELS = json.load(f)

with open(os.path.join(BASE_DIR, 'model', 'categories.json')) as f:
    CATEGORIES = json.load(f)

COMPANIES = sorted(COMPANY_MODELS.keys())
FUEL_TYPES = CATEGORIES['fuels']

CURRENT_YEAR = datetime.now().year
YEAR_RANGE = list(range(CURRENT_YEAR, 1994, -1))


def predict_price(name, company, year, kms_driven, fuel_type):
    """Recreate the trained pipeline's transform + linear regression by hand."""
    vec = np.zeros(len(COEF))
    idx = 0

    if name in NAME_CATEGORIES:
        vec[idx + NAME_CATEGORIES.index(name)] = 1
    idx += len(NAME_CATEGORIES)

    if company in COMPANY_CATEGORIES:
        vec[idx + COMPANY_CATEGORIES.index(company)] = 1
    idx += len(COMPANY_CATEGORIES)

    if fuel_type in FUEL_CATEGORIES:
        vec[idx + FUEL_CATEGORIES.index(fuel_type)] = 1
    idx += len(FUEL_CATEGORIES)

    vec[idx] = year
    vec[idx + 1] = kms_driven

    return float(np.dot(vec, COEF) + INTERCEPT)


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('predict'))
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('predict'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if User.query.filter_by(username=username).first():
            errors.append('That username is already taken.')
        if User.query.filter_by(email=email).first():
            errors.append('An account with that email already exists.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('signup.html')

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Account created successfully. Please sign in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('predict'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter(
            (db.func.lower(User.username) == identifier) | (db.func.lower(User.email) == identifier)
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('predict'))

        flash('Invalid username/email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------
# Prediction routes
# ---------------------------------------------------------------------------
@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    result = None

    if request.method == 'POST':
        company = request.form.get('company', '').strip()
        car_model = request.form.get('car_model', '').strip()
        year = request.form.get('year', '').strip()
        kms_driven = request.form.get('kms_driven', '').strip()
        fuel_type = request.form.get('fuel_type', '').strip()

        errors = []
        if company not in COMPANIES:
            errors.append('Please select a valid manufacturer.')
        if company in COMPANY_MODELS and car_model not in COMPANY_MODELS.get(company, []):
            errors.append('Please select a valid car model for the chosen manufacturer.')
        try:
            year = int(year)
            if year < 1995 or year > CURRENT_YEAR:
                errors.append(f'Year must be between 1995 and {CURRENT_YEAR}.')
        except ValueError:
            errors.append('Please enter a valid year.')
        try:
            kms_driven = int(kms_driven)
            if kms_driven < 0 or kms_driven > 1000000:
                errors.append('Kilometres driven must be between 0 and 1,000,000.')
        except ValueError:
            errors.append('Please enter a valid number for kilometres driven.')
        if fuel_type not in FUEL_TYPES:
            errors.append('Please select a valid fuel type.')

        if errors:
            for e in errors:
                flash(e, 'danger')
        else:
            prediction = predict_price(car_model, company, year, kms_driven, fuel_type)
            prediction = max(0, round(prediction, 2))

            record = Prediction(
                user_id=current_user.id,
                company=company,
                car_model=car_model,
                year=year,
                kms_driven=kms_driven,
                fuel_type=fuel_type,
                predicted_price=prediction
            )
            db.session.add(record)
            db.session.commit()

            result = {
                'price': prediction,
                'company': company,
                'car_model': car_model,
                'year': year,
                'kms_driven': kms_driven,
                'fuel_type': fuel_type
            }

    return render_template(
        'predict.html',
        companies=COMPANIES,
        fuel_types=FUEL_TYPES,
        years=YEAR_RANGE,
        result=result
    )


@app.route('/api/models/<company>')
def api_models(company):
    models_list = COMPANY_MODELS.get(company, [])
    return jsonify(sorted(models_list))


@app.route('/history')
@login_required
def history():
    records = Prediction.query.filter_by(user_id=current_user.id) \
        .order_by(Prediction.created_at.desc()).all()
    return render_template('history.html', records=records)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def init_db():
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

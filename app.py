from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class AreaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area_coordinates = db.Column(db.Text, nullable=False)
    area_name = db.Column(db.String(150), nullable=False)
    water_pollution = db.Column(db.String(100), nullable=True)
    radioactivity = db.Column(db.String(100), nullable=True)
    soil_quality = db.Column(db.String(100), nullable=True)
    living_quality = db.Column(db.String(100), nullable=True)
    ph = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(20), nullable=True)

# Sabit admin kullanıcısı
def create_admin():
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('panel'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['username'] = username
            session['is_admin'] = user.is_admin
            return redirect(url_for('panel'))
        return 'Geçersiz kullanıcı adı veya şifre!'
    return render_template('login.html')

@app.route('/panel')
def panel():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    areas = AreaData.query.all()
    return render_template('panel.html', 
                         areas=areas,
                         is_admin=session.get('is_admin'))

@app.route('/save_area', methods=['POST'])
def save_area():
    if 'username' in session and session.get('is_admin'):
        data = request.get_json()
        
        # Değer kontrolü
        def validate_value(value, min_val, max_val):
            try:
                num = float(value)
                return min(max(num, min_val), max_val)
            except:
                return min_val

        new_area = AreaData(
            area_coordinates=json.dumps(data['coordinates']),
            area_name=data['area_name'],
            water_pollution=str(validate_value(data.get('water_pollution', 0), 0, 10)),
            radioactivity=str(validate_value(data.get('radioactivity', 0), 0, 10)),
            soil_quality=str(validate_value(data.get('soil_quality', 0), 0, 10)),
            living_quality=str(validate_value(data.get('living_quality', 0), 0, 10)),
            ph=str(validate_value(data.get('ph', 7), 0, 14)),
            color=data.get('color', '#3388ff')
        )
        
        db.session.add(new_area)
        db.session.commit()
        return jsonify({'message': 'Alan başarıyla kaydedildi!'}), 200
    return jsonify({'message': 'Yetkisiz erişim!'}), 403

@app.route('/database')
def database():
    areas = AreaData.query.all()
    return render_template('database.html', areas=areas)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)
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
migrate = Migrate(app, db)  # Migrasyon desteği eklendi

# Kullanıcı Modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# Alan Bilgisi Modeli (Yeni sütun: color eklenmiştir)
class AreaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area_coordinates = db.Column(db.Text, nullable=False)  # JSON olarak koordinatlar
    area_name = db.Column(db.String(150), nullable=False)    # Alanın ismi
    water_pollution = db.Column(db.String(100), nullable=True)  # Su kirliliği
    radioactivity = db.Column(db.String(100), nullable=True)    # Radyoaktivite
    soil_quality = db.Column(db.String(100), nullable=True)     # Toprak kalitesi
    living_quality = db.Column(db.String(100), nullable=True)   # Canlı yaşam kalitesi
    ph = db.Column(db.String(50), nullable=True)                # pH değeri
    color = db.Column(db.String(20), nullable=True)             # Alan rengi

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('panel'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        is_admin = 'is_admin' in request.form  # İsteğe bağlı admin yetkisi

        if User.query.filter_by(username=username).first():
            return 'Kullanıcı adı zaten mevcut.'
        
        new_user = User(username=username, password=password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

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
        return 'Geçersiz kullanıcı adı veya şifre.'
    return render_template('login.html')

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'username' not in session:
        return redirect(url_for('login'))
    areas = AreaData.query.all()
    return render_template('panel.html', areas=areas, is_admin=session.get('is_admin'))

@app.route('/save_area', methods=['POST'])
def save_area():
    if 'username' in session and session.get('is_admin'):
        data = request.get_json()
        area_coordinates = json.dumps(data['coordinates'])
        area_name = data['area_name']
        water_pollution = data.get('water_pollution', '')
        radioactivity = data.get('radioactivity', '')
        soil_quality = data.get('soil_quality', '')
        living_quality = data.get('living_quality', '')
        ph = data.get('ph', '')
        color = data.get('color', '#3388ff')  # Varsayılan olarak Leaflet'in varsayılan rengi veya tercih ettiğiniz renk

        new_area = AreaData(
            area_coordinates=area_coordinates,
            area_name=area_name,
            water_pollution=water_pollution,
            radioactivity=radioactivity,
            soil_quality=soil_quality,
            living_quality=living_quality,
            ph=ph,
            color=color
        )
        db.session.add(new_area)
        db.session.commit()

        return jsonify({'message': 'Alan başarıyla kaydedildi.'}), 200

    return jsonify({'message': 'Yetkisiz erişim.'}), 403

@app.route('/database', methods=['GET', 'POST'])
def database():
    query = request.form.get('search_query', '')
    areas = AreaData.query.filter(AreaData.area_name.contains(query)).all() if query else AreaData.query.all()
    return render_template('database.html', areas=areas, search_query=query)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Geliştirme aşamasında; canlı sistemde migrasyon kullanın.
    app.run(debug=True)

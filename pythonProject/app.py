import requests

from datetime import timedelta, datetime, date
from flask import Flask, jsonify,request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1233@127.0.0.1:3306/exercisedb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)


class UserFoodLog(db.Model):
    __tablename__ = 'user_food_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False) 
    food_name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float)
    carbs = db.Column(db.Float)
    protein = db.Column(db.Float)
    fats = db.Column(db.Float)
    quantity = db.Column(db.Float)
    date = db.Column(db.Date, default=date.today)

    user = db.relationship('User', back_populates='food_logs')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    country = db.Column(db.String(50), nullable=True)
    height_cm = db.Column(db.Integer, nullable=True)
    weight_kg = db.Column(db.Integer, nullable=True)
    target_weight_kg = db.Column(db.Integer, nullable=True)
    target_bmi = db.Column(db.Float, nullable=True)
    preferred_sleep_hours = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    water_intake = db.relationship('WaterIntake', uselist=False, back_populates='user', cascade='all, delete-orphan')
    sleep_record = db.relationship('SleepRecord', uselist=False, back_populates='user', cascade='all, delete-orphan')

    # Yeni ilişkiler:
    custom_programs = db.relationship('UserCustomProgram', back_populates='user', cascade='all, delete-orphan')
    daily_program_assignments = db.relationship('UserDailyProgramAssignment', back_populates='user', cascade='all, delete-orphan')

    food_logs = db.relationship('UserFoodLog', back_populates='user', cascade='all, delete-orphan')  # yeni ilişki
    posts = db.relationship('Post', back_populates='user', cascade='all, delete-orphan')  # cascade eklendi


class WaterIntake(db.Model):
    __tablename__ = 'water_intake'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)  # ondelete eklendi
    count = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.Date, default=date.today)

    user = db.relationship('User', back_populates='water_intake')

    def reset_if_needed(self):
        today = date.today()
        if self.last_reset_date != today:
            self.count = 0
            self.last_reset_date = today


class SleepRecord(db.Model):
    __tablename__ = 'sleep_record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)  # ondelete eklendi
    hours_slept = db.Column(db.Float, nullable=True)
    last_reset_date = db.Column(db.Date, default=date.today)

    user = db.relationship('User', back_populates='sleep_record')

    def reset_if_needed(self):
        today = date.today()
        if self.last_reset_date != today:
            self.hours_slept = None
            self.last_reset_date = today


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # ondelete eklendi
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='posts')  # back_populates ile değiştirildi


class UserCustomProgram(db.Model):
    __tablename__ = 'user_custom_program'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # ondelete eklendi
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', back_populates='custom_programs')
    exercises = db.relationship('UserCustomProgramExercise', back_populates='program', cascade='all, delete-orphan')
    daily_assignments = db.relationship('UserDailyProgramAssignment', back_populates='program', cascade='all, delete-orphan')


class UserCustomProgramExercise(db.Model):
    __tablename__ = 'user_custom_program_exercise'
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('user_custom_program.id', ondelete='CASCADE'), nullable=False)  # ondelete eklendi
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)

    program = db.relationship('UserCustomProgram', back_populates='exercises')
    exercise = db.relationship('Exercise')


class UserDailyProgramAssignment(db.Model):
    __tablename__ = 'user_daily_program_assignment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # ondelete eklendi
    program_id = db.Column(db.Integer, db.ForeignKey('user_custom_program.id', ondelete='CASCADE'), nullable=False)  # ondelete eklendi
    date = db.Column(db.Date, nullable=False)

    user = db.relationship('User', back_populates='daily_program_assignments')
    program = db.relationship('UserCustomProgram', back_populates='daily_assignments')


class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)







food_bp = Blueprint('food_bp', __name__, url_prefix='/food')
@app.route('/add-exercise', methods=['POST'])
@jwt_required()
def add_exercise():
    try:
        data = request.get_json()
        name = data.get('name')
        category = data.get('category')
        description = data.get('description')
        image_url = data.get('image_url')

        if not all([name, category, description, image_url]):
            return jsonify({'error': 'Missing Information'}), 400

        exercise = Exercise(
            name=name,
            category=category,
            description=description,
            image_url=image_url
        )

        db.session.add(exercise)
        db.session.commit()

        return jsonify({'message': 'Exercise added to table.'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
@food_bp.route('/search', methods=['GET'])
def search_food():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parametresi eksik'}), 400

    url = f'https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1'
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        return jsonify({'error': 'API hatası', 'details': str(e)}), 500

    results = []
    for item in data.get('products', [])[:5]:
        name = item.get('product_name')
        nutriments = item.get('nutriments', {})
        calories = nutriments.get('energy-kcal_100g')
        protein = nutriments.get('proteins_100g', 0)
        carbs = nutriments.get('carbohydrates_100g', 0)
        fat = nutriments.get('fat_100g', 0)

        if name and calories is not None:
            results.append({
                'name': name,
                'calories_per_100g': calories,
                'protein_per_100g': protein,
                'carbs_per_100g': carbs,
                'fat_per_100g': fat
            })

    if not results:
        return jsonify({'message': 'Sonuç bulunamadı'}), 404

    return jsonify(results)

@food_bp.route('/log', methods=['GET'])
@jwt_required()
def get_food_logs():
    user_id = get_jwt_identity()
    date_str = request.args.get('date')

    if not date_str:
        return jsonify({'error': 'Date parametresi eksik'}), 400

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Tarih formatı yanlış, yyyy-mm-dd olmalı'}), 400

    logs = UserFoodLog.query.filter_by(user_id=user_id, date=date_obj).all()

    results = []
    for log in logs:
        results.append({
            'id': log.id,
            'food_name': log.food_name,
            'calories': log.calories,
            'carbs': log.carbs,
            'protein': log.protein,
            'fats': log.fats,
            'quantity': log.quantity,
            'date': log.date.isoformat()
        })
    print("Food logs response:", results)

    return jsonify(results)
@food_bp.route('/log/<int:log_id>', methods=['DELETE'])
@jwt_required()
def delete_food_log(log_id):
    user_id = get_jwt_identity()
    log = UserFoodLog.query.filter_by(id=log_id, user_id=user_id).first()

    if not log:
        return jsonify({'error': 'Kayıt bulunamadı veya erişim yok'}), 404

    db.session.delete(log)
    db.session.commit()

    return jsonify({'message': 'Yemek kaydı başarıyla silindi!'})

@food_bp.route('/log', methods=['POST'])
@jwt_required()
def add_food_log():
    user_id = get_jwt_identity()
    data = request.get_json()

    food_log = UserFoodLog(
        user_id=user_id,
        food_name=data.get('food_name'),
        calories=data.get('calories'),
        carbs=data.get('carbs'),
        protein=data.get('protein'),
        fats=data.get('fats'),
        quantity=data.get('quantity'),
        date=data.get('date')
    )

    db.session.add(food_log)
    db.session.commit()

    return jsonify({'message': 'Yemek kaydı başarıyla eklendi!'}), 201

@food_bp.route('/logs/calories', methods=['GET'])
@jwt_required()
def get_calories_by_date_range():
    user_id = get_jwt_identity()
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    logs = UserFoodLog.query.filter(
        UserFoodLog.user_id == user_id,
        UserFoodLog.date >= start_date,
        UserFoodLog.date <= end_date
    ).all()

    # Günlük toplam kalorileri hesapla
    daily_calories = {}
    for log in logs:
        day = log.date.strftime('%Y-%m-%d')
        daily_calories[day] = daily_calories.get(day, 0) + log.calories

    # Tarih aralığında boş günleri de 0 kalori ile doldur
    result = []
    current = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    while current <= end:
        day_str = current.strftime('%Y-%m-%d')
        result.append({'date': day_str, 'calories': daily_calories.get(day_str, 0)})
        current += timedelta(days=1)

    return jsonify(result)

# --- CRUD endpointler ---
@app.route('/exercises', methods=['GET'])
@jwt_required()
def get_exercises():
    exercises = Exercise.query.all()
    exercises_list = [{
        'id': e.id,
        'name': e.name,
        'category': e.category,
        'description': e.description,
        'image_url': e.image_url
    } for e in exercises]

    return jsonify(exercises_list)

# Create Program
@app.route('/programs', methods=['POST'])
@jwt_required()
def create_program():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    name = data.get('name')
    image_url = data.get('image_url')

    if not name:
        return jsonify({'error': 'Program name is required'}), 400

    program = UserCustomProgram(user_id=user_id, name=name, image_url=image_url)
    db.session.add(program)
    db.session.commit()

    return jsonify({
        'message': 'Program created successfully',
        'program': {
            'id': program.id,
            'name': program.name,
            'image_url': program.image_url
        }
    }), 201


# Get all programs for user
@app.route('/programs', methods=['GET'])
@jwt_required()
def get_programs():
    user_id = int(get_jwt_identity())
    programs = UserCustomProgram.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'image_url': p.image_url
    } for p in programs])

@app.route('/programs/<int:program_id>/exercises', methods=['POST'])
@jwt_required()
def add_exercises_to_program(program_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    exercise_ids = data.get('exercise_ids', [])

    # Programın kullanıcıya ait olup olmadığını kontrol et
    program = UserCustomProgram.query.filter_by(id=program_id, user_id=user_id).first()
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    # Egzersizleri programa ekle
    for ex_id in exercise_ids:
        # Zaten eklenmişse atla
        exists = UserCustomProgramExercise.query.filter_by(program_id=program_id, exercise_id=ex_id).first()
        if not exists:
            new_link = UserCustomProgramExercise(program_id=program_id, exercise_id=ex_id)
            db.session.add(new_link)

    db.session.commit()
    return jsonify({'message': 'Exercises added to program successfully'})

# Assign program to a date (UserDailyProgramAssignment create)
@app.route('/assign-program', methods=['POST'])
@jwt_required()
def assign_program():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    program_id = data.get('program_id')
    assigned_date_str = data.get('date')

    if not program_id or not assigned_date_str:
        return jsonify({'error': 'program_id and date are required'}), 400

    try:
        assigned_date = datetime.strptime(assigned_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Check if program exists and belongs to user
    program = UserCustomProgram.query.filter_by(id=program_id, user_id=user_id).first()
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    # Check if assignment exists for that date already
    assignment = UserDailyProgramAssignment.query.filter_by(user_id=user_id, date=assigned_date).first()
    if assignment:
        assignment.program_id = program_id  # Güncelle
    else:
        assignment = UserDailyProgramAssignment(user_id=user_id, program_id=program_id, date=assigned_date)
        db.session.add(assignment)

    db.session.commit()
    return jsonify({'message': 'Program assigned to date successfully'})


# Get daily program assignments for user
@app.route('/assignments/exercises', methods=['GET'])
@jwt_required()
def get_exercises_for_assignment():
    user_id = int(get_jwt_identity())
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Kullanıcının o tarihte atadığı programı bul
    assignment = UserDailyProgramAssignment.query.filter_by(user_id=user_id, date=query_date).first()
    if not assignment:
        return jsonify({'error': 'No program assigned for this date'}), 404

    # Programdaki egzersizleri çek
    exercises = (
        db.session.query(Exercise)
        .join(UserCustomProgramExercise, UserCustomProgramExercise.exercise_id == Exercise.id)
        .filter(UserCustomProgramExercise.program_id == assignment.program_id)
        .all()
    )

    exercises_list = [{
        'id': e.id,
        'name': e.name,
        'category': e.category,
        'description': e.description,
        'image_url': e.image_url
    } for e in exercises]

    return jsonify({
        'date': date_str,
        'program_id': assignment.program_id,
        'exercises': exercises_list
    })


@app.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    user_id = int(get_jwt_identity())
    post = Post.query.filter_by(id=post_id, user_id=user_id).first()

    if not post:
        return jsonify({'error': 'Post not found or unauthorized'}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted successfully'})


@app.route('/posts', methods=['GET'])
@jwt_required()
def get_posts():
    user_id = int(get_jwt_identity())
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at.isoformat()
    } for post in posts])


@app.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    title = data.get('title')
    content = data.get('content')

    new_post = Post(user_id=user_id, title=title, content=content)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post created'}), 201


@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed_password = generate_password_hash(data.get('password'))

    user = User(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=email,
        password=hashed_password,
        created_at=datetime.utcnow()
    )

    db.session.add(user)
    db.session.commit()

    water_intake = WaterIntake(user_id=user.id, count=0, last_reset_date=date.today())
    sleep_record = SleepRecord(user_id=user.id, hours_slept=None, last_reset_date=date.today())

    db.session.add(water_intake)
    db.session.add(sleep_record)
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if user and check_password_hash(user.password, data.get('password')):
        token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_admin":user.is_admin
            }
        })
    return jsonify({"error": "Invalid credentials"}), 401


@app.route('/auth/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.age = data.get('age', user.age)
    user.country = data.get('country', user.country)
    user.height_cm = data.get('height_cm', user.height_cm)
    user.weight_kg = data.get('weight_kg', user.weight_kg)
    user.target_weight_kg = data.get('target_weight_kg', user.target_weight_kg)
    user.target_bmi = data.get('target_bmi', user.target_bmi)
    user.preferred_sleep_hours = data.get('preferred_sleep_hours', user.preferred_sleep_hours)

    db.session.commit()

    return jsonify({"message": "User updated successfully"})


@app.route('/auth/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"})


@app.route('/auth/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "age": user.age,
        "country": user.country,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "target_weight_kg": user.target_weight_kg,
        "target_bmi": user.target_bmi,
        "preferred_sleep_hours": user.preferred_sleep_hours,
        "is_admin": user.is_admin
    })

@app.route('/auth/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()

    # Burada istersen admin kontrolü yapabilirsin
    # Örnek:
    # user = User.query.get(current_user_id)
    # if not user.is_admin:
    #     return jsonify({"error": "Unauthorized"}), 403

    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "age": user.age,
            "country": user.country,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "target_weight_kg": user.target_weight_kg,
            "target_bmi": user.target_bmi,
            "preferred_sleep_hours": user.preferred_sleep_hours,
            "is_admin": user.is_admin
        })

    return jsonify(users_list), 200
@app.route('/water-intake', methods=['GET'])
@jwt_required()
def get_water_intake():
    user_id = int(get_jwt_identity())
    record = WaterIntake.query.filter_by(user_id=user_id).first()
    if not record:
        return jsonify({'error': 'Water intake record not found'}), 404

    record.reset_if_needed()
    db.session.commit()

    return jsonify({
        'count': record.count,
        'last_reset_date': record.last_reset_date.isoformat()
    })


@app.route('/water-intake/drink', methods=['POST'])
@jwt_required()
def drink_water():
    user_id = int(get_jwt_identity())
    record = WaterIntake.query.filter_by(user_id=user_id).first()
    if not record:
        return jsonify({'error': 'Water intake record not found'}), 404

    record.reset_if_needed()
    record.count += 1
    db.session.commit()

    return jsonify({'message': 'Water intake incremented', 'count': record.count})


@app.route('/sleep-record', methods=['GET'])
@jwt_required()
def get_sleep_record():
    user_id = int(get_jwt_identity())
    record = SleepRecord.query.filter_by(user_id=user_id).first()
    if not record:
        return jsonify({'error': 'Sleep record not found'}), 404

    record.reset_if_needed()
    db.session.commit()

    return jsonify({
        'hours_slept': record.hours_slept,
        'last_reset_date': record.last_reset_date.isoformat()
    })


@app.route('/sleep-record', methods=['POST'])
@jwt_required()
def set_sleep_record():
    user_id = int(get_jwt_identity())
    record = SleepRecord.query.filter_by(user_id=user_id).first()
    if not record:
        return jsonify({'error': 'Sleep record not found'}), 404

    record.reset_if_needed()
    data = request.get_json()
    hours = data.get('hours_slept')

    if record.hours_slept is not None:
        return jsonify({'error': 'Sleep hours already set for today'}), 400

    if hours is None or type(hours) not in [int, float] or hours < 0:
        return jsonify({'error': 'Invalid hours_slept value'}), 400

    record.hours_slept = hours
    db.session.commit()

    return jsonify({'message': 'Sleep hours recorded', 'hours_slept': record.hours_slept})

app.register_blueprint(food_bp)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

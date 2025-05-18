from datetime import timedelta, datetime, date

from flask import Flask, request, jsonify  # type: ignore
from flask_cors import CORS  # type: ignore
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1233@127.0.0.1:3306/exercisedb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)


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

    water_intake = db.relationship('WaterIntake', uselist=False, back_populates='user', cascade='all, delete-orphan')
    sleep_record = db.relationship('SleepRecord', uselist=False, back_populates='user', cascade='all, delete-orphan')


class WaterIntake(db.Model):
    __tablename__ = 'water_intake'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('posts', lazy=True))


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
                "email": user.email
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
        "preferred_sleep_hours": user.preferred_sleep_hours
    })


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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

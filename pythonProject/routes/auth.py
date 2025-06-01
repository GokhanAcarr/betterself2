from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import datetime, date
from extensions import db
from models.user import User
from models.water import WaterIntake
from models.sleep import SleepRecord

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
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

    # Default records
    db.session.add(WaterIntake(user_id=user.id, count=0, last_reset_date=date.today()))
    db.session.add(SleepRecord(user_id=user.id, hours_slept=None, last_reset_date=date.today()))
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201


@auth_bp.route('/login', methods=['POST'])
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
                "is_admin": user.is_admin
            }
        })
    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
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


@auth_bp.route('/user/<int:user_id>', methods=['PUT'])
@jwt_required()
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


@auth_bp.route('/user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})


@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    users = User.query.all()
    users_list = [{
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
    } for user in users]

    return jsonify(users_list), 200

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, date

from extensions import db
from models import User, WaterIntake, SleepRecord
from flasgger.utils import swag_from

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'description': 'Register a new user account',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['first_name', 'last_name', 'email', 'password'],
            'properties': {
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'email': {'type': 'string'},
                'password': {'type': 'string'}
            }
        }
    }],
    'responses': {
        201: {'description': 'User created successfully'},
        400: {'description': 'Email already exists'}
    }
})
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


@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'description': 'Login and retrieve JWT token',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['email', 'password'],
            'properties': {
                'email': {'type': 'string'},
                'password': {'type': 'string'}
            }
        }
    }],
    'responses': {
        200: {'description': 'Login successful'},
        401: {'description': 'Invalid credentials'}
    }
})
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


@auth_bp.route('/user/<int:user_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['User'],
    'description': 'Update user information (only self)',
    'parameters': [{
        'name': 'user_id',
        'in': 'path',
        'type': 'integer',
        'required': True
    }, {
        'name': 'body',
        'in': 'body',
        'schema': {'type': 'object'}
    }],
    'responses': {
        200: {'description': 'User updated successfully'},
        403: {'description': 'Unauthorized'},
        404: {'description': 'User not found'}
    }
})
def update_user(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

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
@swag_from({
    'tags': ['User'],
    'description': 'Delete user account (only self)',
    'parameters': [{'name': 'user_id', 'in': 'path', 'type': 'integer', 'required': True}],
    'responses': {
        200: {'description': 'User deleted'},
        403: {'description': 'Unauthorized'},
        404: {'description': 'User not found'}
    }
})
def delete_user(user_id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})


@auth_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['User'],
    'description': 'Get own user profile',
    'parameters': [{'name': 'user_id', 'in': 'path', 'type': 'integer', 'required': True}],
    'responses': {
        200: {'description': 'User data returned'},
        403: {'description': 'Unauthorized'},
        404: {'description': 'User not found'}
    }
})
def get_user(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

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


@auth_bp.route('/users', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Admin'],
    'description': 'Get list of all users (admin only)',
    'responses': {
        200: {'description': 'Users returned'},
        403: {'description': 'Unauthorized - Admin only'}
    }
})
def get_all_users():
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)

    if not current_user or not current_user.is_admin:
        return jsonify({"error": "Unauthorized - admin access required"}), 403

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

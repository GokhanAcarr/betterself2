from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Exercise
from flasgger.utils import swag_from

exercise_bp = Blueprint('exercise_bp', __name__, url_prefix='/exercises')


@exercise_bp.route('', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Exercise'],
    'description': 'List all exercises. Optional filter by category.',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'category',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Category to filter (e.g., Cardio, Strength)'
        }
    ],
    'responses': {
        200: {
            'description': 'List of exercises',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'category': {'type': 'string'},
                        'description': {'type': 'string'},
                        'image_url': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def get_exercises():
    user_id = int(get_jwt_identity())
    category = request.args.get('category')

    query = Exercise.query
    if category:
        query = query.filter_by(category=category)

    exercises = query.all()
    result = []
    for ex in exercises:
        result.append({
            "id": ex.id,
            "name": ex.name,
            "description": ex.description,
            "category": ex.category,
            "image_url": ex.image_url
        })

    return jsonify(result), 200


@exercise_bp.route('', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Exercise'],
    'description': 'Create a new exercise (name must be unique)',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['name', 'description', 'category', 'image_url'],
            'properties': {
                'name': {'type': 'string'},
                'description': {'type': 'string'},
                'category': {'type': 'string'},
                'image_url': {'type': 'string'}
            }
        }
    }],
    'responses': {
        201: {'description': 'Exercise created successfully'},
        400: {'description': 'Exercise with this name already exists'}
    }
})
def create_exercise():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    name = data.get('name')
    if Exercise.query.filter_by(name=name).first():
        return jsonify({'error': 'Exercise with this name already exists'}), 400

    exercise = Exercise(
        name=name,
        category=data.get('category'),
        description=data.get('description'),
        image_url=data.get('image_url')
    )

    db.session.add(exercise)
    db.session.commit()

    return jsonify({'message': 'Exercise created successfully'}), 201

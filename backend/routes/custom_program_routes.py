from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models.user_custom_program import UserCustomProgram
from backend.models.user_custom_program_exercise import UserCustomProgramExercise
from backend.models.exercise import Exercise

program_bp = Blueprint('program_bp', __name__, url_prefix='/programs')

@program_bp.route('', methods=['GET'])
@jwt_required()
def get_user_programs():
    user_id = get_jwt_identity()
    programs = UserCustomProgram.query.filter_by(user_id=user_id).all()

    return jsonify([{
        'id': program.id,
        'name': program.name,
        'is_default': program.is_default,
        'image_url': program.image_url
    } for program in programs])

@program_bp.route('', methods=['POST'])
@jwt_required()
def create_program():
    user_id = get_jwt_identity()
    data = request.get_json()

    new_program = UserCustomProgram(
        user_id=user_id,
        name=data.get('name'),
        is_default=data.get('is_default', False),
        image_url=data.get('image_url')
    )

    db.session.add(new_program)
    db.session.commit()

    return jsonify({'message': 'Program başarıyla oluşturuldu'}), 201

@program_bp.route('/<int:program_id>/exercises', methods=['GET'])
@jwt_required()
def get_program_exercises(program_id):
    user_id = get_jwt_identity()

    program = UserCustomProgram.query.filter_by(id=program_id, user_id=user_id).first()
    if not program:
        return jsonify({'error': 'Program bulunamadı'}), 404

    relations = UserCustomProgramExercise.query.filter_by(program_id=program_id).all()
    result = []
    for r in relations:
        exercise = Exercise.query.get(r.exercise_id)
        if exercise:
            result.append({
                'id': exercise.id,
                'name': exercise.name,
                'category': exercise.category,
                'description': exercise.description,
                'image_url': exercise.image_url
            })

    return jsonify(result)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.exercise import Exercise
from models.program import UserCustomProgram, UserCustomProgramExercise, UserDailyProgramAssignment

from datetime import datetime

exercise_bp = Blueprint('exercise_bp', __name__)


@exercise_bp.route('/add-exercise', methods=['POST'])
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


@exercise_bp.route('/exercises', methods=['GET'])
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


@exercise_bp.route('/programs', methods=['POST'])
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


@exercise_bp.route('/programs', methods=['GET'])
@jwt_required()
def get_programs():
    user_id = int(get_jwt_identity())
    programs = UserCustomProgram.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'image_url': p.image_url
    } for p in programs])


@exercise_bp.route('/programs/<int:program_id>/exercises', methods=['POST'])
@jwt_required()
def add_exercises_to_program(program_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    exercise_ids = data.get('exercise_ids', [])

    program = UserCustomProgram.query.filter_by(id=program_id, user_id=user_id).first()
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    for ex_id in exercise_ids:
        exists = UserCustomProgramExercise.query.filter_by(program_id=program_id, exercise_id=ex_id).first()
        if not exists:
            new_link = UserCustomProgramExercise(program_id=program_id, exercise_id=ex_id)
            db.session.add(new_link)

    db.session.commit()
    return jsonify({'message': 'Exercises added to program successfully'})


@exercise_bp.route('/assign-program', methods=['POST'])
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

    program = UserCustomProgram.query.filter_by(id=program_id, user_id=user_id).first()
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    assignment = UserDailyProgramAssignment.query.filter_by(user_id=user_id, date=assigned_date).first()
    if assignment:
        assignment.program_id = program_id
    else:
        assignment = UserDailyProgramAssignment(user_id=user_id, program_id=program_id, date=assigned_date)
        db.session.add(assignment)

    db.session.commit()
    return jsonify({'message': 'Program assigned to date successfully'})


@exercise_bp.route('/assignments/exercises', methods=['GET'])
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

    assignment = UserDailyProgramAssignment.query.filter_by(user_id=user_id, date=query_date).first()
    if not assignment:
        return jsonify({'error': 'No program assigned for this date'}), 404

    exercises = (
        db.session.query(Exercise)
        .join(UserCustomProgramExercise, UserCustomProgramExercise.exercise_id == Exercise.id)
        .filter(UserCustomProgramExercise.program_id == assignment.program_id)
        .all()
    )

    exercises_list = [ {
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

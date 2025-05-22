from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from backend.extensions import db
from backend.models.user_daily_program_assignment import UserDailyProgramAssignment
from backend.models.user_custom_program import UserCustomProgram

assignment_bp = Blueprint('assignment_bp', __name__, url_prefix='/assignments')

@assignment_bp.route('', methods=['GET'])
@jwt_required()
def get_today_assignment():
    user_id = get_jwt_identity()
    today = date.today()

    assignment = UserDailyProgramAssignment.query.filter_by(user_id=user_id, date=today).first()

    if not assignment:
        return jsonify({'message': 'Bugün için program atanmadı'}), 404

    program = UserCustomProgram.query.get(assignment.program_id)
    if not program:
        return jsonify({'error': 'Program bulunamadı'}), 404

    return jsonify({
        'assignment_id': assignment.id,
        'program_id': program.id,
        'program_name': program.name,
        'date': assignment.date.isoformat()
    })

@assignment_bp.route('', methods=['POST'])
@jwt_required()
def assign_program():
    user_id = get_jwt_identity()
    data = request.get_json()
    program_id = data.get('program_id')

    if not program_id:
        return jsonify({'error': 'Program ID gerekli'}), 400

    today = date.today()

    existing = UserDailyProgramAssignment.query.filter_by(user_id=user_id, date=today).first()
    if existing:
        return jsonify({'error': 'Bugün için zaten bir program atanmış'}), 400

    assignment = UserDailyProgramAssignment(
        user_id=user_id,
        program_id=program_id,
        date=today
    )

    db.session.add(assignment)
    db.session.commit()

    return jsonify({'message': 'Program bugüne atandı', 'assignment_id': assignment.id})

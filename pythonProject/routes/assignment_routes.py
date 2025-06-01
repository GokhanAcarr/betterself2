from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import UserDailyProgramAssignment, UserCustomProgram
from datetime import date
from flasgger.utils import swag_from

assignment_bp = Blueprint('assignment_bp', __name__, url_prefix='/assignments')


@assignment_bp.route('', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Assignment'],
    'description': 'Get today\'s assigned custom program for the user',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Assignment data',
            'schema': {
                'type': 'object',
                'properties': {
                    'program_id': {'type': 'integer'},
                    'date': {'type': 'string'}
                }
            }
        },
        404: {'description': 'No assignment for today'}
    }
})
def get_today_assignment():
    user_id = int(get_jwt_identity())
    today = date.today()

    assignment = UserDailyProgramAssignment.query.filter_by(user_id=user_id, date=today).first()

    if not assignment:
        return jsonify({"error": "No assignment found for today"}), 404

    return jsonify({
        "program_id": assignment.program_id,
        "date": str(assignment.date)
    })


@assignment_bp.route('', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Assignment'],
    'description': 'Assign a custom program to the user for today',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['program_id'],
            'properties': {
                'program_id': {'type': 'integer'}
            }
        }
    }],
    'responses': {
        200: {'description': 'Program assigned successfully'},
        404: {'description': 'Custom program not found'}
    }
})
def assign_program():
    user_id = int(get_jwt_identity())
    today = date.today()

    data = request.get_json()
    program_id = data.get('program_id')

    program = UserCustomProgram.query.filter_by(id=program_id, user_id=user_id).first()
    if not program:
        return jsonify({"error": "Custom program not found"}), 404

    existing = UserDailyProgramAssignment.query.filter_by(user_id=user_id, date=today).first()
    if existing:
        existing.program_id = program_id
    else:
        new_assignment = UserDailyProgramAssignment(user_id=user_id, program_id=program_id, date=today)
        db.session.add(new_assignment)

    db.session.commit()
    return jsonify({"message": "Program assigned successfully"})

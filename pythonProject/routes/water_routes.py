from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date

from extensions import db
from models import WaterIntake
from flasgger.utils import swag_from

water_bp = Blueprint('water_bp', __name__, url_prefix='/water-intake')


@water_bp.route('', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Water'],
    'description': 'Get today\'s water intake and percentage of goal (default goal: 8 glasses)',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Water intake data',
            'schema': {
                'type': 'object',
                'properties': {
                    'count': {'type': 'integer'},
                    'target': {'type': 'integer'},
                    'percentage': {'type': 'number'}
                }
            }
        },
        404: {'description': 'Water intake record not found'}
    }
})
def get_water_intake():
    user_id = int(get_jwt_identity())
    today = date.today()

    record = WaterIntake.query.filter_by(user_id=user_id).first()
    if not record:
        return jsonify({'error': 'Water intake record not found'}), 404

    if record.last_reset_date != today:
        record.count = 0
        record.last_reset_date = today
        db.session.commit()

    target = 8
    percent = round((record.count / target) * 100) if target else 0

    return jsonify({
        "count": record.count,
        "target": target,
        "percentage": percent
    })


@water_bp.route('/drink', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Water'],
    'description': 'Increment water intake count by 1 for today',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Water intake incremented',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'count': {'type': 'integer'}
                }
            }
        },
        404: {'description': 'Water intake record not found'}
    }
})
def drink_water():
    user_id = int(get_jwt_identity())
    today = date.today()

    record = WaterIntake.query.filter_by(user_id=user_id).first()
    if not record:
        return jsonify({'error': 'Water intake record not found'}), 404

    if record.last_reset_date != today:
        record.count = 1
        record.last_reset_date = today
    else:
        record.count += 1

    db.session.commit()

    return jsonify({'message': 'Water intake incremented', 'count': record.count})

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date

from extensions import db
from models import SleepRecord, User
from flasgger.utils import swag_from

sleep_bp = Blueprint('sleep_bp', __name__, url_prefix='/sleep')


@sleep_bp.route('', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Sleep'],
    'description': 'Get today\'s sleep record and comparison with preferred sleep hours',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Sleep info',
            'schema': {
                'type': 'object',
                'properties': {
                    'hours_slept': {'type': 'number'},
                    'preferred_sleep_hours': {'type': 'number'},
                    'difference': {'type': 'number'}
                }
            }
        }
    }
})
def get_sleep_record():
    user_id = int(get_jwt_identity())
    today = date.today()

    sleep = SleepRecord.query.filter_by(user_id=user_id).first()
    user = User.query.get(user_id)

    if not sleep or not user:
        return jsonify({'error': 'Record not found'}), 404

    if sleep.last_reset_date != today:
        sleep.hours_slept = None
        sleep.last_reset_date = today
        db.session.commit()

    return jsonify({
        "hours_slept": sleep.hours_slept,
        "preferred_sleep_hours": user.preferred_sleep_hours,
        "difference": (sleep.hours_slept or 0) - (user.preferred_sleep_hours or 0)
    })


@sleep_bp.route('', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Sleep'],
    'description': 'Set today\'s sleep duration in hours',
    'security': [{'Bearer': []}],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'required': ['hours_slept'],
            'properties': {
                'hours_slept': {'type': 'number'}
            }
        }
    }],
    'responses': {
        200: {'description': 'Sleep record updated'}
    }
})
def update_sleep_record():
    user_id = int(get_jwt_identity())
    today = date.today()

    data = request.get_json()
    hours = data.get('hours_slept')

    record = SleepRecord.query.filter_by(user_id=user_id).first()
    if not record:
        return jsonify({'error': 'Record not found'}), 404

    if record.last_reset_date != today:
        record.last_reset_date = today

    record.hours_slept = hours
    db.session.commit()

    return jsonify({'message': 'Sleep record updated successfully'})

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.sleep import SleepRecord
from datetime import date

sleep_bp = Blueprint('sleep_bp', __name__, url_prefix='/sleep-record')


@sleep_bp.route('', methods=['GET'])
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


@sleep_bp.route('', methods=['POST'])
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

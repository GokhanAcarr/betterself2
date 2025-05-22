from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from backend.extensions import db
from backend.models.water_sleep import SleepRecord

sleep_bp = Blueprint('sleep_bp', __name__, url_prefix='/sleep')

@sleep_bp.route('', methods=['GET'])
@jwt_required()
def get_sleep_record():
    user_id = get_jwt_identity()
    record = SleepRecord.query.filter_by(user_id=user_id, date=date.today()).first()

    if not record:
        record = SleepRecord(user_id=user_id, hours_slept=None, date=date.today())
        db.session.add(record)
        db.session.commit()

    return jsonify({
        'hours_slept': record.hours_slept,
        'date': record.date.isoformat()
    })

@sleep_bp.route('', methods=['POST'])
@jwt_required()
def set_sleep_record():
    user_id = get_jwt_identity()
    data = request.get_json()
    hours = data.get('hours_slept')

    if hours is None or type(hours) not in [int, float] or hours < 0:
        return jsonify({'error': 'Geçersiz saat bilgisi'}), 400

    record = SleepRecord.query.filter_by(user_id=user_id, date=date.today()).first()

    if not record:
        record = SleepRecord(user_id=user_id, hours_slept=hours, date=date.today())
        db.session.add(record)
    elif record.hours_slept is not None:
        return jsonify({'error': 'Bugün için uyku kaydı zaten mevcut'}), 400
    else:
        record.hours_slept = hours

    db.session.commit()
    return jsonify({'message': 'Uyku süresi kaydedildi', 'hours_slept': record.hours_slept})

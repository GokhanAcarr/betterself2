from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from backend.extensions import db
from backend.models.water_sleep import WaterIntake

water_bp = Blueprint('water_bp', __name__, url_prefix='/water')

@water_bp.route('/water-intake', methods=['GET'])
@jwt_required()
def get_water_intake():
    user_id = get_jwt_identity()
    record = WaterIntake.query.filter_by(user_id=user_id, date=date.today()).first()

    if not record:
        # Yeni gün için otomatik kayıt oluştur
        record = WaterIntake(user_id=user_id, count=0, date=date.today())
        db.session.add(record)
        db.session.commit()

    return jsonify({
        'count': record.count,
        'date': record.date.isoformat()
    })

@water_bp.route('/drink', methods=['POST'])
@jwt_required()
def drink_water():
    user_id = get_jwt_identity()
    record = WaterIntake.query.filter_by(user_id=user_id, date=date.today()).first()

    if not record:
        record = WaterIntake(user_id=user_id, count=1, date=date.today())
        db.session.add(record)
    else:
        record.count += 1

    db.session.commit()
    return jsonify({'message': 'Su içme kaydı eklendi', 'count': record.count})

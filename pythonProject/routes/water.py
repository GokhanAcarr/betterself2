from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.water import WaterIntake
from datetime import date

water_bp = Blueprint('water_bp', __name__, url_prefix='/water-intake')


@water_bp.route('', methods=['GET'])
@jwt_required()
def get_water_intake():
    user_id = int(get_jwt_identity())
    record = WaterIntake.query.filter_by(user_id=user_id).first()
    if not record:
        return jsonify({'error': 'Water intake record not found'}), 404

    record.reset_if_needed()
    db.session.commit()

    return jsonify({
        'count': record.count,
        'last_reset_date': record.last_reset_date.isoformat()
    })


@water_bp.route('/drink', methods=['POST'])
@jwt_required()
def drink_water():
    user_id = int(get_jwt_identity())
    record = WaterIntake.query.filter_by(user_id=user_id).first()
    if not record:
        return jsonify({'error': 'Water intake record not found'}), 404

    record.reset_if_needed()
    record.count += 1
    db.session.commit()

    return jsonify({'message': 'Water intake incremented', 'count': record.count})

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from extensions import db
from models import WaterIntake, SleepRecord, UserFoodLog, User
from flasgger.utils import swag_from

stats_bp = Blueprint('stats_bp', __name__, url_prefix='/stats')


@stats_bp.route('/summary', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Stats'],
    'description': 'Get last 7 days summary of water intake, sleep hours, and calories',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Weekly summary',
            'schema': {
                'type': 'object',
                'properties': {
                    'water_intake': {'type': 'array', 'items': {'type': 'integer'}},
                    'sleep_hours': {'type': 'array', 'items': {'type': 'number'}},
                    'calories': {'type': 'array', 'items': {'type': 'number'}}
                }
            }
        }
    }
})
def get_weekly_summary():
    user_id = int(get_jwt_identity())
    today = datetime.utcnow().date()

    summary = {
        "water_intake": [],
        "sleep_hours": [],
        "calories": []
    }

    for i in range(7):
        day = today - timedelta(days=i)

        # Water
        water = WaterIntake.query.filter_by(user_id=user_id, last_reset_date=day).first()
        summary["water_intake"].append(water.count if water else 0)

        # Sleep
        sleep = SleepRecord.query.filter_by(user_id=user_id, last_reset_date=day).first()
        summary["sleep_hours"].append(sleep.hours_slept if sleep and sleep.hours_slept else 0)

        # Calories
        logs = UserFoodLog.query.filter_by(user_id=user_id, date=day).all()
        total_calories = sum([log.calories or 0 for log in logs])
        summary["calories"].append(total_calories)

    return jsonify(summary)

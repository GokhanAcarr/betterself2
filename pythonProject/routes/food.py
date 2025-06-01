from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.food_log import UserFoodLog
import requests
from datetime import datetime, timedelta, date

food_bp = Blueprint('food_bp', __name__, url_prefix='/food')


@food_bp.route('/search', methods=['GET'])
def search_food():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parametresi eksik'}), 400

    url = f'https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1'
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        return jsonify({'error': 'API hatası', 'details': str(e)}), 500

    results = []
    for item in data.get('products', [])[:5]:
        name = item.get('product_name')
        nutriments = item.get('nutriments', {})
        calories = nutriments.get('energy-kcal_100g')
        protein = nutriments.get('proteins_100g', 0)
        carbs = nutriments.get('carbohydrates_100g', 0)
        fat = nutriments.get('fat_100g', 0)

        if name and calories is not None:
            results.append({
                'name': name,
                'calories_per_100g': calories,
                'protein_per_100g': protein,
                'carbs_per_100g': carbs,
                'fat_per_100g': fat
            })

    if not results:
        return jsonify({'message': 'Sonuç bulunamadı'}), 404

    return jsonify(results)


@food_bp.route('/log', methods=['GET'])
@jwt_required()
def get_food_logs():
    user_id = get_jwt_identity()
    date_str = request.args.get('date')

    if not date_str:
        return jsonify({'error': 'Date parametresi eksik'}), 400

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Tarih formatı yanlış, yyyy-mm-dd olmalı'}), 400

    logs = UserFoodLog.query.filter_by(user_id=user_id, date=date_obj).all()

    results = []
    for log in logs:
        results.append({
            'id': log.id,
            'food_name': log.food_name,
            'calories': log.calories,
            'carbs': log.carbs,
            'protein': log.protein,
            'fats': log.fats,
            'quantity': log.quantity,
            'date': log.date.isoformat()
        })

    return jsonify(results)


@food_bp.route('/log', methods=['POST'])
@jwt_required()
def add_food_log():
    user_id = get_jwt_identity()
    data = request.get_json()

    food_log = UserFoodLog(
        user_id=user_id,
        food_name=data.get('food_name'),
        calories=data.get('calories'),
        carbs=data.get('carbs'),
        protein=data.get('protein'),
        fats=data.get('fats'),
        quantity=data.get('quantity'),
        date=data.get('date')
    )

    db.session.add(food_log)
    db.session.commit()

    return jsonify({'message': 'Yemek kaydı başarıyla eklendi!'}), 201


@food_bp.route('/log/<int:log_id>', methods=['DELETE'])
@jwt_required()
def delete_food_log(log_id):
    user_id = get_jwt_identity()
    log = UserFoodLog.query.filter_by(id=log_id, user_id=user_id).first()

    if not log:
        return jsonify({'error': 'Kayıt bulunamadı veya erişim yok'}), 404

    db.session.delete(log)
    db.session.commit()

    return jsonify({'message': 'Yemek kaydı başarıyla silindi!'})


@food_bp.route('/logs/calories', methods=['GET'])
@jwt_required()
def get_calories_by_date_range():
    user_id = get_jwt_identity()
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    logs = UserFoodLog.query.filter(
        UserFoodLog.user_id == user_id,
        UserFoodLog.date >= start_date,
        UserFoodLog.date <= end_date
    ).all()

    daily_calories = {}
    for log in logs:
        day = log.date.strftime('%Y-%m-%d')
        daily_calories[day] = daily_calories.get(day, 0) + log.calories

    result = []
    current = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    while current <= end:
        day_str = current.strftime('%Y-%m-%d')
        result.append({'date': day_str, 'calories': daily_calories.get(day_str, 0)})
        current += timedelta(days=1)

    return jsonify(result)

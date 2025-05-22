from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
from backend.extensions import db
from backend.models.food_log import UserFoodLog

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
        calories = item.get('nutriments', {}).get('energy-kcal_100g')
        if name and calories:
            results.append({
                'name': name,
                'calories_per_100g': calories
            })

    if not results:
        return jsonify({'message': 'Sonuç bulunamadı'}), 404

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
        quantity=data.get('quantity')
    )

    db.session.add(food_log)
    db.session.commit()

    return jsonify({'message': 'Yemek kaydı başarıyla eklendi!'}), 201

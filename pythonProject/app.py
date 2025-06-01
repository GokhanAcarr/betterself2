from flask import Flask
from dotenv import load_dotenv
import os

from extensions import db, jwt, cors
from models import *  # tüm modeller yükleniyor
from routes import (
    auth_bp,
    food_bp,
    post_bp,
    exercise_bp,
    assignment_bp,
    water_bp,
    sleep_bp,
    stats_bp,
)
from flasgger import Swagger

# .env dosyasını yükle
load_dotenv()

# Swagger Authorize için özel template
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "BetterSelf API",
        "description": "Swagger UI for testing JWT-protected routes",
        "version": "1.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: Bearer <your_token>"
        }
    },
    "security": [{"Bearer": []}]
}

app = Flask(__name__)

# Swagger başlat
Swagger(app, template=swagger_template)

# CORS başlat
cors.init_app(app, resources={r"/*": {"origins": "*"}})

# Config ayarları
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 1 gün

# Extensionları başlat
db.init_app(app)
jwt.init_app(app)

# Blueprints (tüm route dosyalarını ekle)
app.register_blueprint(auth_bp)
app.register_blueprint(food_bp)
app.register_blueprint(post_bp)
app.register_blueprint(exercise_bp)
app.register_blueprint(assignment_bp)
app.register_blueprint(water_bp)
app.register_blueprint(sleep_bp)
app.register_blueprint(stats_bp)

@app.route('/')
def index():
    return {"message": "BetterSelf API is running."}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

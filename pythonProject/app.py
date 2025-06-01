from flask import Flask
from extensions import db, jwt, cors
from datetime import timedelta

# Blueprint'leri import et
from routes.auth import auth_bp
from routes.exercise import exercise_bp
from routes.food import food_bp
from routes.post import post_bp
from routes.sleep import sleep_bp
from routes.water import water_bp

def create_app():
    app = Flask(__name__)

    # Konfigürasyonlar
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1233@127.0.0.1:3306/exercisedb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'secret-key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

    # Extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})

    # Blueprint kayıtları
    app.register_blueprint(auth_bp)
    app.register_blueprint(exercise_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(sleep_bp)
    app.register_blueprint(water_bp)

    # Veritabanını oluştur
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

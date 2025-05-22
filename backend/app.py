from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.extensions import db
from backend.routes import all_blueprints  # routes klasöründeki tüm blueprintleri import ettik

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Config ayarları
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:002312@127.0.0.1:3306/betterself'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'secret-key'

    # Extensions
    db.init_app(app)
    JWTManager(app)

    # Register routes
    for bp in all_blueprints:
        app.register_blueprint(bp)

    # Debug route
    @app.route('/debug')
    def debug():
        return jsonify({"message": "Backend çalışıyor!"})

    return app

# Ana çalışma bloğu
if __name__ == '__main__':
    from pathlib import Path
    import os
    os.chdir(Path(__file__).parent)

    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)

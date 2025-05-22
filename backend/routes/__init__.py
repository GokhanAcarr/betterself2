from .auth_routes import auth_bp
from .post_routes import post_bp
from .food_routes import food_bp
from .water_routes import water_bp
from .sleep_routes import sleep_bp
from .custom_program_routes import program_bp
from .assignment_routes import assignment_bp

all_blueprints = [
    auth_bp,
    post_bp,
    food_bp,
    water_bp,
    sleep_bp,
    program_bp,
    assignment_bp
]

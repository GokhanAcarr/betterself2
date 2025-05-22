from backend.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer)
    country = db.Column(db.String(50))
    height_cm = db.Column(db.Integer)
    weight_kg = db.Column(db.Integer)
    target_weight_kg = db.Column(db.Integer)
    target_bmi = db.Column(db.Float)
    preferred_sleep_hours = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='user', lazy=True)
    food_logs = db.relationship('UserFoodLog', backref='user', lazy=True)
    water_intakes = db.relationship('WaterIntake', backref='user', lazy=True)
    sleep_records = db.relationship('SleepRecord', backref='user', lazy=True)
    custom_programs = db.relationship('UserCustomProgram', backref='user', lazy=True)
    daily_assignments = db.relationship('UserDailyProgramAssignment', backref='user', lazy=True)
    admins = db.relationship('Admin', backref='user', lazy=True)

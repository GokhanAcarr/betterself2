from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    country = db.Column(db.String(50), nullable=True)
    height_cm = db.Column(db.Integer, nullable=True)
    weight_kg = db.Column(db.Integer, nullable=True)
    target_weight_kg = db.Column(db.Integer, nullable=True)
    target_bmi = db.Column(db.Float, nullable=True)
    preferred_sleep_hours = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    # İlişkiler (diğer modeller tanımlandıkça aktifleşir)
    water_intake = db.relationship('WaterIntake', uselist=False, back_populates='user', cascade='all, delete-orphan')
    sleep_record = db.relationship('SleepRecord', uselist=False, back_populates='user', cascade='all, delete-orphan')

    custom_programs = db.relationship('UserCustomProgram', back_populates='user', cascade='all, delete-orphan')
    daily_program_assignments = db.relationship('UserDailyProgramAssignment', back_populates='user', cascade='all, delete-orphan')

    food_logs = db.relationship('UserFoodLog', back_populates='user', cascade='all, delete-orphan')
    posts = db.relationship('Post', back_populates='user', cascade='all, delete-orphan')
    
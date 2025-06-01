from datetime import datetime, date
from extensions import db

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
    is_admin = db.Column(db.Boolean, default=False)

    water_intake = db.relationship('WaterIntake', uselist=False, back_populates='user', cascade='all, delete-orphan')
    sleep_record = db.relationship('SleepRecord', uselist=False, back_populates='user', cascade='all, delete-orphan')
    food_logs = db.relationship('UserFoodLog', back_populates='user', cascade='all, delete-orphan')
    posts = db.relationship('Post', back_populates='user', cascade='all, delete-orphan')
    custom_programs = db.relationship('UserCustomProgram', back_populates='user', cascade='all, delete-orphan')
    daily_program_assignments = db.relationship('UserDailyProgramAssignment', back_populates='user', cascade='all, delete-orphan')


class WaterIntake(db.Model):
    __tablename__ = 'water_intake'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    count = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.Date, default=date.today)

    user = db.relationship('User', back_populates='water_intake')

    def reset_if_needed(self):
        today = date.today()
        if self.last_reset_date != today:
            self.count = 0
            self.last_reset_date = today


class SleepRecord(db.Model):
    __tablename__ = 'sleep_record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    hours_slept = db.Column(db.Float)
    last_reset_date = db.Column(db.Date)

    user = db.relationship('User', back_populates='sleep_record')

    def reset_if_needed(self):
        today = date.today()
        if self.last_reset_date != today:
            self.hours_slept = None
            self.last_reset_date = today

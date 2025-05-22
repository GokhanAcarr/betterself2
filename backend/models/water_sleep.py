from backend.extensions import db
from datetime import date

class WaterIntake(db.Model):
    __tablename__ = 'water_intake'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    count = db.Column(db.Integer, default=0)

class SleepRecord(db.Model):
    __tablename__ = 'sleep_record'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    hours_slept = db.Column(db.Float)

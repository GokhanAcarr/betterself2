from extensions import db
from datetime import date

class UserFoodLog(db.Model):
    __tablename__ = 'user_food_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float)
    carbs = db.Column(db.Float)
    protein = db.Column(db.Float)
    fats = db.Column(db.Float)
    quantity = db.Column(db.Float)
    date = db.Column(db.Date, default=date.today)

    user = db.relationship('User', back_populates='food_logs')

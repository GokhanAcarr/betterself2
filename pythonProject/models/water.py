from extensions import db
from datetime import date

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

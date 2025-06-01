from extensions import db
from datetime import date

class SleepRecord(db.Model):
    __tablename__ = 'sleep_record'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    hours_slept = db.Column(db.Float, nullable=True)
    last_reset_date = db.Column(db.Date, default=date.today)

    user = db.relationship('User', back_populates='sleep_record')

    def reset_if_needed(self):
        today = date.today()
        if self.last_reset_date != today:
            self.hours_slept = None
            self.last_reset_date = today

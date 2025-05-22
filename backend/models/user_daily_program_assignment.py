from backend.extensions import db
from datetime import date

class UserDailyProgramAssignment(db.Model):
    __tablename__ = 'user_daily_program_assignment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('user_custom_program.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)

from backend.extensions import db

class UserCustomProgram(db.Model):
    __tablename__ = 'user_custom_program'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(255))

    exercises = db.relationship('UserCustomProgramExercise', backref='program', lazy=True)
    daily_assignments = db.relationship('UserDailyProgramAssignment', backref='program', lazy=True)

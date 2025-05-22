from backend.extensions import db

class UserCustomProgramExercise(db.Model):
    __tablename__ = 'user_custom_program_exercise'

    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('user_custom_program.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)

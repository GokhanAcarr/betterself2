from extensions import db

class UserCustomProgram(db.Model):
    __tablename__ = 'user_custom_program'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255))

    user = db.relationship('User', back_populates='custom_programs')
    exercises = db.relationship('UserCustomProgramExercise', back_populates='program', cascade='all, delete-orphan')
    daily_assignments = db.relationship('UserDailyProgramAssignment', back_populates='program', cascade='all, delete-orphan')


class UserCustomProgramExercise(db.Model):
    __tablename__ = 'user_custom_program_exercise'

    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('user_custom_program.id', ondelete='CASCADE'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)

    program = db.relationship('UserCustomProgram', back_populates='exercises')
    exercise = db.relationship('Exercise')


class UserDailyProgramAssignment(db.Model):
    __tablename__ = 'user_daily_program_assignment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('user_custom_program.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)

    user = db.relationship('User', back_populates='daily_program_assignments')
    program = db.relationship('UserCustomProgram', back_populates='daily_assignments')

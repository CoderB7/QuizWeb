from extentions.extension import db
from flask_login import UserMixin
from sqlalchemy import JSON, and_, or_, not_, column, asc, desc
from sqlalchemy.orm import relationship


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    second_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    education = db.Column(db.String(100), nullable=False)
    quizzes_uploaded = db.Column(db.Integer, nullable=False)
    number_of_solved_quizzes = db.Column(db.Integer, nullable=False)
    # This will act like a List of Quiz objects attached to each User.
    # The "teacher" refers to the teacher property in the Quiz class.
    quizs = relationship("Quiz", back_populates="teacher")
    # This will act like a List of Answers objects attached to each Student User.
    # The "student" refers to the teacher property in the Quiz class.
    answers = relationship("StudentAnswers", back_populates="student")


class Quiz(db.Model):
    __tablename__ = "quiz_database"
    id = db.Column(db.Integer, primary_key=True)
    # Create Foreign Key
    teacher_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # Create reference to the User object, the "quizs" refers to the quizs property in the User class.
    teacher = relationship("User", back_populates="quizs")
    title = db.Column(db.String(150), nullable=False, unique=True)
    question_type = db.Column(db.String(150), nullable=False)
    question_amount = db.Column(db.Integer, nullable=False)
    number_of_answers_each_question = db.Column(db.Integer, nullable=False)
    question_data = db.Column(JSON, nullable=False)
    total_score = db.Column(db.Integer, nullable=False)
    created_time = db.Column(db.String(150), nullable=False)
    number_of_views = db.Column(db.Integer, nullable=False)


class StudentAnswers(db.Model):
    __tablename__ = "student_answers"
    id = db.Column(db.Integer, primary_key=True)
    # Create a Foreign Key
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # Create reference to the User object, the "answers" refers to the answers property in the User class.
    student = relationship("User", back_populates="answers")
    solved_quiz_id = db.Column(db.Integer, nullable=False)
    subject_title = db.Column(db.String(150), nullable=False)
    question_type = db.Column(db.String(150), nullable=False)
    student_answers_json = db.Column(JSON, nullable=False)
    solved_time = db.Column(db.String(150), nullable=False)
    student_score = db.Column(db.Integer, nullable=False)
    total_score = db.Column(db.Integer, nullable=False)

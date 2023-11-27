from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, current_user, logout_user
from extentions.extension import db
from modal_database.modal import Quiz, StudentAnswers, User
from functions.functions import find_average_point, find_max_point, find_min_point

users = Blueprint("users", __name__, template_folder="templates", static_folder="static", static_url_path="assets")


@users.route("/teacher", methods=["GET", "POST"])
def teacher_page():
    print(current_user.first_name)
    return render_template("user/teacher.html", current_user=current_user)


@users.route('/student')
def student_page():
    result_q = db.session.execute(db.select(Quiz).order_by(Quiz.id))
    quizs = result_q.fetchall()
    student_id = current_user.id

    # Top Quizzes list
    top_quizs = [item for item in quizs if item[0].number_of_views > 2]

    # To get quizzes that are NOT SOLVED
    result_answers = db.session.execute(db.select(StudentAnswers).filter(StudentAnswers.student_id == student_id)).all()
    if result_answers:

        # Algorithm for sorting if current_user solved quiz that exists in Top Quizzes
        top_solved_quizs = []
        top_not_solved_quizs = []
        solved_quiz_id_s = [item[0].solved_quiz_id for item in result_answers]
        print(solved_quiz_id_s)
        for q_uiz in top_quizs:
            if q_uiz[0].id in solved_quiz_id_s:
                top_solved_quizs.append(q_uiz)
            else:
                top_not_solved_quizs.append(q_uiz)
        #######

        # Algorithm for displaying quizzes that are NOT solved -> for Preview page
        quizs_not_solved = []
        for q_uiz in quizs:
            if q_uiz[0].id not in solved_quiz_id_s:
                quizs_not_solved.append(q_uiz)
        print(quizs_not_solved)
        return render_template("user/student.html", current_user=current_user, quizs=quizs_not_solved,
                               top_solved_quizs=top_solved_quizs, top_not_solved_quizs=top_not_solved_quizs)
        ######

    else:
        return render_template("user/student.html", current_user=current_user, quizs=quizs, top_quizs=top_quizs)


@users.route('/student/student_profile')
def student_profile():
    if current_user.is_authenticated and current_user.education == "Student":
        result_s = db.session.execute(db.select(User).where(User.id == current_user.id))
        user = result_s.scalar()
        print(user)

        # -> For finding max, min, average points
        result_a = db.session.execute(db.select(StudentAnswers).filter(StudentAnswers.student_id == current_user.id)).all()
        student_points = [item[0].student_score for item in result_a]
        max_point = find_max_point(student_points)
        min_point = find_min_point(student_points)
        average_point = find_average_point(student_points)

        return render_template("user/student_profile.html", user=user, max_point=max_point,
                               min_point=min_point, average_point=average_point)
    else:
        abort(403)


@users.route('/teacher/teacher_profile')
def teacher_profile():
    if current_user.is_authenticated and current_user.education == "Teacher":
        result_t = db.session.execute(db.select(User).where(User.id == current_user.id))
        user = result_t.scalar()
        print(user)
        return render_template("user/teacher_profile.html", user=user)
    else:
        abort(403)

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from extentions.extension import db, login_manager
from modal_database.modal import User, StudentAnswers, Quiz
from forms import QuizForm, QuestionForm
from flask_login import current_user
from functions.functions import score_calculator, total_score_
from sqlalchemy import and_, desc
import datetime as dt

quiz_data = None
question_order_number = 0
number_of_answers_each_question = 0
number_of_answers = 0


# Json Exception
class JsonError(Exception):
    def __init__(self, exception):
        self.exception = exception

    # __str__ is to print() the value
    def __str__(self):
        return repr(self.exception)


quiz_functionality = Blueprint("quiz_functionality", __name__, template_folder="templates", static_folder="static",
                               static_url_path="asset")


@login_manager.user_loader
def load_user(user_id):
    # Load the user from either Teacher or Student models.
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    return user


@quiz_functionality.route("/", methods=["GET", "POST"])
def quiz():
    global number_of_answers_each_question, question_order_number, quiz_data
    is_visible = False
    form = QuizForm()
    if current_user.is_authenticated:
        if request.method == "POST":
            print('GO')
            try:
                if not request.is_json:
                    raise JsonError("Unsupported Media type")
                quiz_data = request.get_json()
                print("try")
                print(quiz_data)
            except JsonError:
                quiz_data = request.form
                print("jsonerror")
                print(quiz_data)
                number_of_answers_each_question = int(quiz_data["num_answer_field"])
                is_visible = True
            return render_template("quiz/quiz.html", current_user=current_user, quiz_form=form, quiz_data=quiz_data,
                                   mode="form", is_visible=is_visible)
        elif request.method == "GET":
            question_order_number = 0
            return render_template("quiz/quiz.html", current_user=current_user, quiz_form=form,
                                   mode="form", is_visible=is_visible)
    else:
        flash("You need to log in or register in order to create quiz", category="error")
        return redirect(url_for('login'))


# Step 5: Create a route to dynamically add forms
@quiz_functionality.route('/new_form', methods=['GET', 'POST'])
def new_form():
    global number_of_answers_each_question, question_order_number
    q_form = QuestionForm()
    dynamic_answers = []
    if current_user.is_authenticated:
        if request.method == "POST":
            pass
        elif request.method == "GET":
            question_order_number = question_order_number + 1
            # dynamic_answers = q_form.retrieve_answer_fields(number_of_answers_each_question)
            # Append new answer fields to the dynamic_answers field
            for _ in range(number_of_answers_each_question):
                q_form.dynamic_answers.append_entry()
        return render_template('quiz/new_form_template_1.html', question_form=q_form,
                               n_o_answers=number_of_answers_each_question, q_number=question_order_number,
                               dynamic_answers=dynamic_answers)
    else:
        abort(403)


@quiz_functionality.route('/quiz_preview/<mode>/<quiz_id>', methods=["GET"])
def quiz_preview_page(mode, quiz_id):
    global quiz_data, question_order_number, number_of_answers_each_question
    if current_user.is_authenticated:
        if mode == "preview_specific":
            result = db.session.execute(db.select(Quiz).where(Quiz.id == quiz_id))
            quiz_to_preview = result.scalar()
            ans_if_structure = "dynamic_answers-"
            quiz_data = quiz_to_preview.question_data
            return render_template("quiz/quiz_preview.html", mode_to_preview="preview_specific",
                                   quiz_data=quiz_data, quiz_to_preview=quiz_to_preview,
                                   n_o_answers=quiz_to_preview.number_of_answers_each_question,
                                   ans_if_structure=ans_if_structure)
        else:
            try:
                print(quiz_data)
                print(mode)
                form_data = quiz_data['1']
                question_data = dict(list(quiz_data.items())[1:])
                print(question_data)
                if mode == "upload":
                    print("entered")
                    # Getting Exact time <Created>
                    time = dt.datetime.now().strftime("%b %d, %Y")

                    total_points = total_score_(question_data)
                    new_quiz = Quiz(
                        title=form_data['quiz_title'],
                        teacher=current_user,
                        question_type=form_data['question_type'],
                        question_amount=question_order_number,
                        number_of_answers_each_question=number_of_answers_each_question,
                        question_data=question_data,
                        created_time=time,
                        number_of_views=0,
                        total_score=total_points,
                    )
                    question_order_number = 0
                    db.session.add(new_quiz)
                    db.session.commit()

                    # -> Updating quizzes_uploaded in User
                    user_to_update = db.session.execute(db.select(User).where(User.id == current_user.id)).scalar()
                    inc_1 = int(user_to_update.quizzes_uploaded)
                    user_to_update.quizzes_uploaded = inc_1 + 1
                    db.session.commit()

                    return redirect(url_for('users.teacher_page'))
                elif mode == "preview":
                    print("hi")
                    ans_if_structure = "dynamic_answers-"
                    return render_template("quiz/quiz_preview.html", quiz_data=question_data, form_data=form_data,
                                           n_o_answers=number_of_answers_each_question, mode_to_preview="preview",
                                           ans_if_structure=ans_if_structure)
            except TypeError and KeyError:
                return redirect(url_for('quiz_functionality.quiz'))
    else:
        flash("You need to log in or register to preview quiz")
        return redirect(url_for('authenticate.login'))


@quiz_functionality.route('/quiz_list')
def quiz_list():
    result = db.session.execute(db.select(User).where(User.email == current_user.email))
    user = result.scalar()
    print(user.quizs)
    return render_template("quiz/quiz_list.html", user_quizs=user.quizs, number_of_quizs=(len(user.quizs)))


@quiz_functionality.route('/delete_quiz/<quiz_id>')
def delete_quiz(quiz_id):
    result = db.session.execute(db.select(Quiz).where(Quiz.id == quiz_id))
    quiz_to_delete = result.scalar()
    db.session.delete(quiz_to_delete)
    db.session.commit()
    return redirect(url_for('quiz_functionality.quiz_list'))


# Solving quiz process
@quiz_functionality.route('/attempt_quiz/<q_id>', methods=["GET", "POST"])
def solve_quiz(q_id):
    inc_1 = 0
    inc_2 = 0
    if current_user.is_authenticated:
        if request.method == "POST":
            # After submission
            result = db.session.execute(db.select(Quiz).where(Quiz.id == int(q_id)))
            quiz_to_solve = result.scalar()
            question_data = quiz_to_solve.question_data
            student_answers = request.get_json()
            quiz_title = quiz_to_solve.title
            score_data = score_calculator(student_answers, question_data)

            # -> Getting Exact time <Solved>
            time = dt.datetime.now().strftime("%B %d, %Y")

            new_answers = StudentAnswers(
                student=current_user,
                solved_quiz_id=q_id,
                subject_title=quiz_title,
                question_type=quiz_to_solve.question_type,
                student_answers_json=student_answers,
                solved_time=time,
                student_score=score_data[0],
                total_score=score_data[1],
            )
            db.session.add(new_answers)
            db.session.commit()

            # -> Updating number_of_views column in Quiz database
            quiz_to_update = db.session.execute(db.select(Quiz).where(Quiz.id == q_id)).scalar()
            inc_1 = int(quiz_to_update.number_of_views)
            quiz_to_update.number_of_views = inc_1 + 1
            db.session.commit()

            # -> Updating number_of_solved_quizzes in User database
            user_to_update = db.session.execute(db.select(User).where(User.id == current_user.id)).scalar()
            inc_2 = int(user_to_update.number_of_solved_quizzes)
            user_to_update.number_of_solved_quizzes = inc_2 + 1
            db.session.commit()
            return jsonify({'success': True, 'score': score_data[0], 'total_score': score_data[1],
                            'quiz_title': quiz_title})
        elif request.method == "GET":
            result = db.session.execute(db.select(Quiz).where(Quiz.id == int(q_id)))
            quiz_to_solve = result.scalar()
            question_data = quiz_to_solve.question_data
            question_amount = quiz_to_solve.question_amount
            question_title = quiz_to_solve.title
            ans_if_structure = "dynamic_answers-"
            n_o_answers = quiz_to_solve.number_of_answers_each_question
            return render_template("quiz/quiz_solve_from_zero.html", current_user=current_user, quiz_id=q_id,
                                   quiz_data=question_data, question_amount=question_amount,
                                   question_title=question_title,
                                   ans_if_structure=ans_if_structure, n_o_answers=int(n_o_answers))
    else:
        abort(403)


# Quiz over
@quiz_functionality.route('/quiz_over')
def quiz_over():
    score = request.args.get('score')
    total_score = request.args.get('total_score')
    quiz_title = request.args.get('quiz_title')
    return render_template("quiz/quiz_over.html", score=score, total_score=total_score, quiz_title=quiz_title)


@quiz_functionality.route('/teacher/quiz_results')
def quiz_results():
    if current_user.is_authenticated:
        # -> Getting quizzes that are created by current_teacher
        result_t = db.session.execute(db.select(User).where(User.id == current_user.id))
        teacher = result_t.scalar()
        teacher_quizzes = teacher.quizs

        # -> Getting students who solved these quizzes
        teacher_quizzes_id = [q.id for q in teacher_quizzes]
        result_a = db.session.execute(db.select(StudentAnswers).order_by(StudentAnswers.solved_quiz_id))
        all_quizzes_result = result_a.scalars()
        quiz_result_students = [q_answer for q_answer in all_quizzes_result if q_answer.solved_quiz_id in
                                teacher_quizzes_id]
        print(quiz_result_students)
        return render_template("quiz/quiz_results_reviews.html", current_user=current_user,
                               teacher_quizzes=teacher_quizzes,
                               quiz_result_students=quiz_result_students)
    else:
        abort(403)


@quiz_functionality.route('/quiz_results/student_answer/<student_id>/<quiz_id>')
def student_answer(student_id, quiz_id):
    if current_user.is_authenticated:
        from_page = request.args.get('from_page')
        # -> Getting answers that belongs to current_student
        result_a = db.session.execute(db.select(StudentAnswers).filter(and_(StudentAnswers.student_id == student_id,
                                                                            StudentAnswers.solved_quiz_id == quiz_id)))
        student_answer_data = result_a.scalar()
        student_answers = student_answer_data.student_answers_json

        # -> Getting quiz data that current_student solved
        result_q = db.session.execute(db.select(Quiz).where(Quiz.id == student_answer_data.solved_quiz_id))
        q_data = result_q.scalar()
        print(q_data.title)
        questions = q_data.question_data
        print(questions)
        return render_template("quiz/student_answers_page.html", student_answer_data=student_answer_data,
                               quiz_data=q_data,
                               questions=questions, student_answers=student_answers, from_page=from_page)
    else:
        abort(403)


@quiz_functionality.route('/student/quiz_history')
def solved_quizzes_history():
    if current_user.is_authenticated:
        # -> Getting quizzes id that current_student solved
        # -> Sorting quizzes according to their solved_time
        # -> Query and print data, sorted by solved_time in descending order
        results_desc = db.session.query(StudentAnswers).order_by(desc(StudentAnswers.solved_time)).all()
        solved_quizzes_answers = [item for item in results_desc if item.student_id == current_user.id]
        solved_quizzes_time = [item.solved_time for item in solved_quizzes_answers]

        # -> Algorithm for finding exact dates in descending order
        star_times = []
        star = solved_quizzes_time[0]
        star_times.append(star)
        for n in range(0, len(solved_quizzes_time)):
            if n == len(solved_quizzes_time)-1:
                pass
            elif star != solved_quizzes_time[n+1]:
                star_times.append(solved_quizzes_time[n+1])
                star = solved_quizzes_time[n+1]
            elif star == solved_quizzes_time[n+1]:
                n += 1

        return render_template("quiz/solved_quizzes_history.html", solved_quizzes=solved_quizzes_answers,
                               star_times=star_times)
    else:
        abort(403)



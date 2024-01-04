import datetime as dt
import html
import json
import ast

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    jsonify,
)
from flask_login import current_user
from sqlalchemy import and_, desc

from extentions.extension import db, login_manager
from forms import MultipleChoiceForm, TrueFalseForm, QuestionFormMCh, QuestionFormTF, OpenTriviaForm
from functions.functions import score_calculator, total_score_, trivia_request, shuffle_answers
from modal_database.modal import User, StudentAnswers, Quiz

quiz_data = None
question_order_number = 0
number_of_answers_each_question = 0
number_of_answers = 0
quiz_type = None
flag_new_form_m_ch = True


# Json Exception
class JsonError(Exception):
    def __init__(self, exception):
        self.exception = exception

    # __str__ is to print() the value
    def __str__(self):
        return repr(self.exception)


quiz_functionality = Blueprint(
    "quiz_functionality",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="asset",
)


@login_manager.user_loader
def load_user(user_id):
    # Load the user from either Teacher or Student models.
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    return user


@quiz_functionality.route("/quiz_choice", methods=["GET", "POST"])
def quiz_choice():
    if current_user.is_authenticated:
        if request.method == "GET":
            return render_template("quiz/quiz_example.html")


@quiz_functionality.route("/true_false", methods=["GET", "POST"])
def t_f_form():
    global question_order_number, quiz_data, quiz_type
    form = TrueFalseForm()
    is_visible = True
    if current_user.is_authenticated:
        if request.method == "POST":
            print("GO_TRUE_FALSE")
            quiz_data = request.get_json()
            print(quiz_data)
            is_visible = True
            return render_template(
                "quiz/t_f_form.html",
                current_user=current_user,
                quiz_form=form,
                quiz_data=quiz_data,
                is_visible=is_visible,
            )
        elif request.method == "GET":
            question_order_number = 0
            quiz_type = "True/False"
            return render_template(
                "quiz/t_f_form.html",
                current_user=current_user,
                quiz_form=form,
                is_visible=is_visible,
            )
            pass
    else:
        flash(
            "You need to log in or register in order to create quiz", category="error"
        )
        return redirect(url_for("login"))


@quiz_functionality.route("/multiple_choice", methods=["GET", "POST"])
def m_ch_form():
    global number_of_answers_each_question, question_order_number, quiz_data, quiz_type
    is_visible = False
    form = MultipleChoiceForm()
    if current_user.is_authenticated:
        if request.method == "POST":
            print("GO")
            quiz_data = request.get_json()
            print(quiz_data)
            return None
        if request.method == "GET":
            question_order_number = 0
            quiz_type = "Multiple Choice"
            return render_template(
                "quiz/m_ch_form.html",
                current_user=current_user,
                quiz_form=form,
                mode="form",
                is_visible=is_visible,
            )
    else:
        flash(
            "You need to log in or register in order to create quiz", category="error"
        )
        return redirect(url_for("login"))


@quiz_functionality.route("/true_false/new_form_t_f")
def new_form_t_f():
    global question_order_number
    q_form = QuestionFormTF()
    if current_user.is_authenticated:
        if request.method == "GET":
            question_order_number = question_order_number + 1
        return render_template(
            "quiz/new_form_template_tf.html",
            question_form=q_form,
            q_number=question_order_number,
        )
    else:
        abort(403)


# Step 5: Create a route to dynamically add forms
@quiz_functionality.route("/multiple_choice/new_form_m_ch", methods=["GET", "POST"])
def new_form_m_ch():
    global number_of_answers_each_question, question_order_number, flag_new_form_m_ch
    q_form = QuestionFormMCh()
    dynamic_answers = []

    if current_user.is_authenticated:
        if request.method == "POST":
            data = request.get_json()
            print(data)
            if flag_new_form_m_ch:
                number_of_answers_each_question = int(data['1']["num_answer_field"])
                flag_new_form_m_ch = False
            question_order_number = question_order_number + 1
            print(number_of_answers_each_question)
            # dynamic_answers = q_form.retrieve_answer_fields(number_of_answers_each_question)
            # Append new answer fields to the dynamic_answers field
            for _ in range(number_of_answers_each_question):
                q_form.dynamic_answers.append_entry()

        return render_template(
            "quiz/new_form_template_mch.html",
            question_form=q_form,
            n_o_answers=number_of_answers_each_question,
            q_number=question_order_number,
            dynamic_answers=dynamic_answers,
        )
    else:
        abort(403)


@quiz_functionality.route("/add_from_library", methods=["POST", "GET"])
def add_from_library():
    global quiz_data, quiz_type
    form = OpenTriviaForm()
    if current_user.is_authenticated:
        if request.method == "POST":
            quiz_data = request.get_json()
            question_amount = quiz_data['1']["question_amount"]
            category = quiz_data['1']["category"]
            difficulty = quiz_data['1']["difficulty"]
            quiz_type = quiz_data['1']["type"]
            point = quiz_data['1']["point"]
            result = trivia_request(question_amount, category, difficulty, quiz_type)
            quiz_data = [point, result]
            # return redirect(url_for("quiz_functionality.from_library_preview_page", mode="preview", quiz_id="none"))

            question_amount = len(quiz_data[0])

            return jsonify(
                {
                    "success": True,
                    "quiz_data": json.dumps(quiz_data[1]),
                    "mode_to_preview": "preview",
                    "quiz_type": quiz_type,
                    "question_amount": question_amount,
                }
            )
        if request.method == "GET":
            return render_template(
                "quiz/add_from_library.html",
                current_user=current_user,
                trivia_form=form
            )


@quiz_functionality.route("/add_from_library/<mode>/<quiz_id>")
def from_library_preview_page(mode, quiz_id):
    global quiz_data, quiz_type
    if current_user.is_authenticated:
        if mode == "preview_specific":
            result = db.session.execute(db.select(Quiz).where(Quiz.id == quiz_id))
            quiz_to_preview = result.scalar()
            quiz_data = quiz_to_preview.question_data
            question_amount = len(quiz_data)
            answer_data = []
            for question in quiz_data:
                question_answer = question["correct_answer"]
                incorrect_answers = question["incorrect_answers"]
                incorrect_answers.append(question_answer)
                answer_data.append(incorrect_answers)
            print(answer_data)
            point = int(quiz_to_preview.total_score / quiz_to_preview.question_amount)
            if quiz_to_preview.question_type == "multiple":
                quiz_type_temp = "Multiple Choice"
            else:
                quiz_type_temp = "True/False"
            print(quiz_type_temp)
            return render_template(
                "quiz/from_library_preview.html",
                mode_to_preview="preview_specific",
                quiz_type=quiz_type_temp,
                shuffled_answers=answer_data,
                quiz_data=quiz_data,
                quiz_to_preview=quiz_to_preview,
                point=point,
                question_amount=question_amount,
            )
        else:
            answer_data = []
            for question in quiz_data[1]:
                question["correct_answer"] = html.unescape(question["correct_answer"])
                question["question"] = html.unescape(question["question"])
                question["incorrect_answers"] = html.unescape(question["incorrect_answers"])
                question_answer = question["correct_answer"]
                incorrect_answers = question["incorrect_answers"]
                result_2 = shuffle_answers(question_answer, incorrect_answers, quiz_type)
                answer_data.append(result_2)
            question_amount = len(quiz_data[1])

            if quiz_type == "multiple":
                answer_amount = 4
            else:
                answer_amount = 2

            if mode == "upload":
                time = dt.datetime.now().strftime("%b %d, %Y")
                total_points = int(quiz_data[0]) * question_amount
                new_quiz = Quiz(
                    title=quiz_data[1][0]["category"],
                    teacher=current_user,
                    question_type=quiz_type,
                    question_amount=question_amount,
                    number_of_answers_each_question=answer_amount,
                    question_data=quiz_data[1],
                    created_time=time,
                    number_of_views=0,
                    total_score=total_points,
                )
                db.session.add(new_quiz)
                db.session.commit()

                # -> Updating quizzes_uploaded in User
                user_to_update = db.session.execute(
                    db.select(User).where(User.id == current_user.id)
                ).scalar()
                inc_1 = int(user_to_update.quizzes_uploaded)
                user_to_update.quizzes_uploaded = inc_1 + 1
                db.session.commit()

                return redirect(url_for("users.teacher_page"))
            elif mode == "preview":
                if quiz_type == "multiple":
                    quiz_type_temp = "Multiple Choice"
                else:
                    quiz_type_temp = "True/False"
                return render_template(
                    "quiz/from_library_preview.html",
                    quiz_data=quiz_data[1],
                    mode_to_preview="preview",
                    quiz_type=quiz_type_temp,
                    shuffled_answers=answer_data,
                    question_amount=question_amount,
                    point=quiz_data[0],
                )
    else:
        flash("You need to log in or register to preview quiz")
        return redirect(url_for("authenticate.login"))


@quiz_functionality.route("/true_false/<mode>/<quiz_id>")
def t_f_preview_page(mode, quiz_id):
    global quiz_data, question_order_number, quiz_type
    if current_user.is_authenticated:
        if mode == "preview_specific":
            result = db.session.execute(db.select(Quiz).where(Quiz.id == quiz_id))
            quiz_to_preview = result.scalar()
            quiz_data = quiz_to_preview.question_data
            return render_template(
                "quiz/t_f_preview.html",
                mode_to_preview="preview_specific",
                quiz_type=quiz_to_preview.question_type,
                quiz_data=quiz_data,
                quiz_to_preview=quiz_to_preview,
            )
        else:
            try:
                print(quiz_data)
                print(mode)
                form_data = quiz_data["1"]
                question_data = dict(list(quiz_data.items())[1:])
                print(question_data)
                if mode == "upload":
                    # Getting Exact time <Created>
                    time = dt.datetime.now().strftime("%b %d, %Y")

                    total_points = total_score_(question_data)
                    new_quiz = Quiz(
                        title=form_data["quiz_title"],
                        teacher=current_user,
                        question_type=quiz_type,
                        question_amount=question_order_number,
                        number_of_answers_each_question=2,
                        question_data=question_data,
                        created_time=time,
                        number_of_views=0,
                        total_score=total_points
                    )
                    question_order_number = 0
                    db.session.add(new_quiz)
                    db.session.commit()

                    # -> Updating quizzes_uploaded in User
                    user_to_update = db.session.execute(
                        db.select(User).where(User.id == current_user.id)
                    ).scalar()
                    inc_1 = int(user_to_update.quizzes_uploaded)
                    user_to_update.quizzes_uploaded = inc_1 + 1
                    db.session.commit()

                    return redirect(url_for("users.teacher_page"))
                elif mode == "preview":
                    # print("hi_true_false")
                    return render_template(
                        "quiz/t_f_preview.html",
                        quiz_data=question_data,
                        form_data=form_data,
                        mode_to_preview="preview",
                        quiz_type=quiz_type,
                    )
            except TypeError and KeyError:
                redirect(url_for("quiz_functionality.t_f_form"))
    else:
        flash("You need to log in or register to preview quiz")
        return redirect(url_for("authenticate.login"))


@quiz_functionality.route("/quiz_preview/<mode>/<quiz_id>", methods=["GET"])
def m_ch_preview_page(mode, quiz_id):
    global quiz_data, question_order_number, number_of_answers_each_question, quiz_type
    if current_user.is_authenticated:
        print("why")
        if mode == "preview_specific":
            result = db.session.execute(db.select(Quiz).where(Quiz.id == quiz_id))
            quiz_to_preview = result.scalar()
            ans_if_structure = "dynamic_answers-"
            quiz_data = quiz_to_preview.question_data
            return render_template(
                "quiz/m_ch_preview.html",
                mode_to_preview="preview_specific",
                quiz_type=quiz_to_preview.question_type,
                quiz_data=quiz_data,
                quiz_to_preview=quiz_to_preview,
                n_o_answers=quiz_to_preview.number_of_answers_each_question,
                ans_if_structure=ans_if_structure,
            )
        else:
            try:
                print(quiz_data)
                # here
                print(mode)
                form_data = quiz_data["1"]
                question_data = dict(list(quiz_data.items())[1:])
                print(question_data)
                if mode == "upload":
                    print("entered")
                    # Getting Exact time <Created>
                    time = dt.datetime.now().strftime("%b %d, %Y")
                    print(question_order_number)
                    total_points = total_score_(question_data)
                    new_quiz = Quiz(
                        title=form_data["quiz_title"],
                        teacher=current_user,
                        question_type=quiz_type,
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
                    user_to_update = db.session.execute(
                        db.select(User).where(User.id == current_user.id)
                    ).scalar()
                    inc_1 = int(user_to_update.quizzes_uploaded)
                    user_to_update.quizzes_uploaded = inc_1 + 1
                    db.session.commit()

                    return redirect(url_for("users.teacher_page"))
                elif mode == "preview":
                    print("hi")
                    ans_if_structure = "dynamic_answers-"
                    return render_template(
                        "quiz/m_ch_preview.html",
                        quiz_data=question_data,
                        form_data=form_data,
                        n_o_answers=number_of_answers_each_question,
                        mode_to_preview="preview",
                        ans_if_structure=ans_if_structure,
                        quiz_type=quiz_type,
                    )
            except TypeError and KeyError:
                return redirect(url_for("quiz_functionality.m_ch_form"))
    else:
        flash("You need to log in or register to preview quiz")
        return redirect(url_for("authenticate.login"))


@quiz_functionality.route("/quiz_list")
def quiz_list():
    result = db.session.execute(db.select(User).where(User.email == current_user.email))
    user = result.scalar()
    print(user.quizs)
    own_work = []
    from_library = []
    for quiz in user.quizs:
        try:
            if quiz.question_data[0]['type'] == "boolean" or quiz.question_data[0]['type'] == "multiple":
                if quiz.question_type == "multiple":
                    quiz.question_type = "Multiple Choice"
                else:
                    quiz.question_type = "True/False"
                from_library.append(quiz)
        except KeyError:
            if quiz.question_data["Q1"]:
                own_work.append(quiz)
    number_of_own_quizzes = len(own_work)
    number_of_from_library = len(from_library)
    return render_template(
        "quiz/quiz_list.html", own_work=own_work, from_library=from_library,
        number_of_own_quizzes=number_of_own_quizzes, number_of_from_library=number_of_from_library
    )


@quiz_functionality.route("/delete_quiz/<quiz_id>")
def delete_quiz(quiz_id):
    result = db.session.execute(db.select(Quiz).where(Quiz.id == quiz_id))
    quiz_to_delete = result.scalar()
    db.session.delete(quiz_to_delete)
    db.session.commit()
    return redirect(url_for("quiz_functionality.quiz_list"))


# Solving quiz process
@quiz_functionality.route("/attempt_quiz/<q_id>", methods=["GET", "POST"])
def solve_quiz(q_id):
    if current_user.is_authenticated:
        if request.method == "POST":
            form_library = None
            # After submission
            result = db.session.execute(db.select(Quiz).where(Quiz.id == int(q_id)))
            quiz_to_solve = result.scalar()
            question_data = quiz_to_solve.question_data
            student_answers = request.get_json()
            quiz_title = quiz_to_solve.title
            try:
                if question_data[0]["type"] == "boolean" or question_data[0]["type"] == "multiple":
                    from_library = True
            except KeyError:
                if question_data["Q1"]:
                    from_library = False

            #  checking whether quiz from library or not
            if from_library:
                point = int(quiz_to_solve.total_score / quiz_to_solve.question_amount)
                score_data = score_calculator(student_answers, question_data, from_library, point)
            else:
                score_data = score_calculator(student_answers, question_data, from_library, point=0)

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
            quiz_to_update = db.session.execute(
                db.select(Quiz).where(Quiz.id == q_id)
            ).scalar()
            inc_1 = int(quiz_to_update.number_of_views)
            quiz_to_update.number_of_views = inc_1 + 1
            db.session.commit()

            # -> Updating number_of_solved_quizzes in User database
            user_to_update = db.session.execute(
                db.select(User).where(User.id == current_user.id)
            ).scalar()
            inc_2 = int(user_to_update.number_of_solved_quizzes)
            user_to_update.number_of_solved_quizzes = inc_2 + 1
            db.session.commit()
            return jsonify(
                {
                    "success": True,
                    "score": score_data[0],
                    "total_score": score_data[1],
                    "quiz_title": quiz_title,
                }
            )
        elif request.method == "GET":
            result = db.session.execute(db.select(Quiz).where(Quiz.id == int(q_id)))
            quiz_to_solve = result.scalar()
            question_data = quiz_to_solve.question_data
            question_amount = quiz_to_solve.question_amount
            question_title = quiz_to_solve.title
            quiz_type = quiz_to_solve.question_type
            form_library = None
            try:
                if question_data[0]["type"] == "boolean" or question_data[0]["type"] == "multiple":
                    from_library = True
            except KeyError:
                if question_data["Q1"]:
                    from_library = False

            #  checking whether quiz from library or not
            if from_library:
                n_o_answers = quiz_to_solve.number_of_answers_each_question

                #  shuffling process
                answer_data = []
                for question in question_data:
                    question_answer = question["correct_answer"]
                    incorrect_answers = question["incorrect_answers"]
                    result_2 = shuffle_answers(question_answer, incorrect_answers, quiz_type)
                    answer_data.append(result_2)
                ####

                if quiz_type == "multiple":
                    return render_template(
                        "quiz/from_library_quiz_solve.html",
                        current_user=current_user,
                        quiz_id=q_id,
                        quiz_data=question_data,
                        shuffled_answers=answer_data,
                        question_amount=question_amount,
                        question_title=question_title,
                        n_o_answers=int(n_o_answers),
                    )
                elif quiz_type == "boolean":
                    return render_template(
                        "quiz/from_library_quiz_solve.html",
                        current_user=current_user,
                        quiz_id=q_id,
                        quiz_data=question_data,
                        shuffled_answers=answer_data,
                        question_amount=question_amount,
                        question_title=question_title,
                        n_o_answers=int(n_o_answers)
                    )
            else:
                if quiz_type == "Multiple Choice":
                    ans_if_structure = "dynamic_answers-"
                    n_o_answers = quiz_to_solve.number_of_answers_each_question
                    return render_template(
                        "quiz/m_ch_quiz_solve.html",
                        current_user=current_user,
                        quiz_id=q_id,
                        quiz_data=question_data,
                        question_amount=question_amount,
                        question_title=question_title,
                        ans_if_structure=ans_if_structure,
                        n_o_answers=int(n_o_answers),
                    )
                elif quiz_type == "True/False":
                    result = db.session.execute(db.select(Quiz).where(Quiz.id == int(q_id)))
                    quiz_to_solve = result.scalar()
                    question_data = quiz_to_solve.question_data
                    question_amount = quiz_to_solve.question_amount
                    question_title = quiz_to_solve.title
                    return render_template(
                        "quiz/t_f_quiz_solve.html",
                        current_user=current_user,
                        quiz_id=q_id,
                        quiz_data=question_data,
                        question_amount=question_amount,
                        question_title=question_title
                    )
    else:
        abort(403)


# Quiz over
@quiz_functionality.route("/quiz_over")
def quiz_over():
    score = request.args.get("score")
    total_score = request.args.get("total_score")
    quiz_title = request.args.get("quiz_title")
    return render_template(
        "quiz/quiz_over.html",
        score=score,
        total_score=total_score,
        quiz_title=quiz_title,
    )


@quiz_functionality.route("/teacher/quiz_results")
def quiz_results():
    if current_user.is_authenticated:
        # -> Getting quizzes that are created by current_teacher
        result_t = db.session.execute(db.select(User).where(User.id == current_user.id))
        teacher = result_t.scalar()
        teacher_quizzes = teacher.quizs

        # -> Getting students who solved these quizzes
        teacher_quizzes_id = [q.id for q in teacher_quizzes]
        result_a = db.session.execute(
            db.select(StudentAnswers).order_by(StudentAnswers.solved_quiz_id)
        )
        all_quizzes_result = result_a.scalars()
        quiz_result_students = [
            q_answer
            for q_answer in all_quizzes_result
            if q_answer.solved_quiz_id in teacher_quizzes_id
        ]
        print(quiz_result_students)
        return render_template(
            "quiz/quiz_results_reviews.html",
            current_user=current_user,
            teacher_quizzes=teacher_quizzes,
            quiz_result_students=quiz_result_students,
        )
    else:
        abort(403)


@quiz_functionality.route("/quiz_results/student_answer/<student_id>/<quiz_id>")
def student_answer(student_id, quiz_id):
    if current_user.is_authenticated:
        from_page = request.args.get("from_page")
        # -> Getting answers that belongs to current_student
        result_a = db.session.execute(
            db.select(StudentAnswers).filter(
                and_(
                    StudentAnswers.student_id == student_id,
                    StudentAnswers.solved_quiz_id == quiz_id,
                )
            )
        )
        student_answer_data = result_a.scalar()
        student_answers = student_answer_data.student_answers_json
        print(student_answers)
        # -> Getting quiz data that current_student solved
        result_q = db.session.execute(
            db.select(Quiz).where(Quiz.id == student_answer_data.solved_quiz_id)
        )
        q_data = result_q.scalar()
        print(q_data.title)
        questions = q_data.question_data
        question_amount = len(questions)
        if q_data.question_type == "multiple" or q_data.question_type == "boolean":
            from_library = True
            point = int(q_data.total_score / question_amount)
            key = "Q"
        else:
            from_library = False
        print(questions)
        return render_template(
            "quiz/student_answers_page.html",
            student_answer_data=student_answer_data,
            quiz_data=q_data,
            from_library=from_library,
            question_amount=question_amount,
            questions=questions,
            student_answers=student_answers,
            from_page=from_page,
            point=point,
            key=key,
        )
    else:
        abort(403)


@quiz_functionality.route("/student/quiz_history")
def solved_quizzes_history():
    if current_user.is_authenticated:
        # -> Getting quizzes id that current_student solved
        # -> Sorting quizzes according to their solved_time
        # -> Query and print data, sorted by solved_time in descending order
        results_desc = (
            db.session.query(StudentAnswers)
            .order_by(desc(StudentAnswers.solved_time))
            .all()
        )
        solved_quizzes_answers = [
            item for item in results_desc if item.student_id == current_user.id
        ]
        solved_quizzes_time = [item.solved_time for item in solved_quizzes_answers]
        print(solved_quizzes_time)
        if not solved_quizzes_time:
            no_data = True
            star_times = None
        else:
            no_data = False
            # -> Algorithm for finding exact dates in descending order
            star_times = []
            star = solved_quizzes_time[0]
            star_times.append(star)
            for n in range(0, len(solved_quizzes_time)):
                if n == len(solved_quizzes_time) - 1:
                    pass
                elif star != solved_quizzes_time[n + 1]:
                    star_times.append(solved_quizzes_time[n + 1])
                    star = solved_quizzes_time[n + 1]
                elif star == solved_quizzes_time[n + 1]:
                    n += 1

        return render_template(
            "quiz/solved_quizzes_history.html",
            solved_quizzes=solved_quizzes_answers,
            star_times=star_times,
            no_data=no_data,
        )
    else:
        abort(403)


@quiz_functionality.route("/example")
def example():
    return render_template("quiz/quiz_example.html")

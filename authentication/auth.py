from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
from extentions.extension import db, login_manager
from modal_database.modal import User
from flask_login import login_user, current_user, logout_user
import datetime as dt

authenticate = Blueprint(
    "authenticate",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="assets",
)


# @login_manager.user_loader
# def load_user(user_id):
#     # Load the user from either Teacher or Student models.
#     user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
#     return user


@authenticate.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    data = request.form
    result = None
    new_user = None
    if request.method == "POST":
        result = db.session.execute(db.select(User).where(User.email == data["email"]))
        user = result.scalar()
        if user:
            flash(
                "You've already signed up with that email, log in instead!",
                category="error",
            )
            return redirect(url_for("authenticate.login"))
        else:
            hash_and_salted_password = generate_password_hash(
                data["password"],
                method="pbkdf2:sha256",
                salt_length=8,
            )
            new_user = User(
                first_name=data["first_name"],
                second_name=data["second_name"],
                email=data["email"],
                phone_number=data["phone_number"],
                password=hash_and_salted_password,
                education=data["education"],
                number_of_solved_quizzes=0,
                quizzes_uploaded=0,
            )
            db.session.add(new_user)
            db.session.commit()
            # This line will authenticate the user with Flask-Login
            login_user(new_user)
            if data["education"] == "Teacher":
                return redirect(url_for("users.teacher_page"))
            elif data["education"] == "Student":
                return redirect(url_for("users.student_page"))
    return render_template(
        "authentication/register.html", form=register_form, current_user=current_user
    )


@authenticate.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    data = request.form
    if request.method == "POST":
        password = data["password"]
        result = db.session.execute(db.select(User).where(User.email == data["email"]))
        user = result.scalar()
        print(data["email"])
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.", category="error")
            return redirect(url_for("authenticate.login"))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash("Password Incorrect, please try again", category="error")
            return redirect(url_for("authenticate.login"))
        elif user.education == "Teacher":
            login_user(user)
            return redirect(url_for("users.teacher_page", current_user=current_user))
        elif user.education == "Student":
            login_user(user)
            print(current_user.first_name)
            return redirect(url_for("users.student_page", current_user=current_user))
    return render_template(
        "authentication/login.html", form=login_form, current_user=current_user
    )


@authenticate.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("general.home"))


@authenticate.before_request
def before_request():
    session.permanent = True
    authenticate.permanent_session_lifetime = dt.timedelta(minutes=10)
    session.modified = True

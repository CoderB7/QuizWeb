import dotenv
from flask import Flask
from sqlalchemy.event import listen
from flask_bootstrap import Bootstrap5
from modal_database.modal import User, Quiz, StudentAnswers
from authentication.auth import authenticate
from general.general import general
from extentions.extension import db, login_manager
from user.user import users
from quiz.quiz import quiz_functionality
import os

dotenv.load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
Bootstrap5(app)

# Configure Flask login
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    # Load the user from either Teacher or Student models.
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    return user


# CONNECT TO DB
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://quiz_web_db_nlc5_user:T6RvlGoPNvvfkOj6fndKwFftr7dhAugU@dpg-cm26gd0cmk4c73cnv68g-a.singapore-postgres.render.com:5432/quiz_web_db_nlc5"
db.init_app(app)

# Registering Blueprints
app.register_blueprint(authenticate, url_prefix="/authenticate")
app.register_blueprint(general, url_prefix="")
app.register_blueprint(users, url_prefix="/user")
app.register_blueprint(quiz_functionality, url_prefix="/quiz")


with app.app_context():
    # Attach the event listener
    db.create_all()


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, port=5001)

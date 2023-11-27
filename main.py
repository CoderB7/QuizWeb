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
# '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('FLASK_KEY')
app.config["TESTING"] = True
Bootstrap5(app)

# Configure Flask login
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    # Load the user from either Teacher or Student models.
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    return user


# CONNECT TO DB
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI", "sqlite:///quiz.db")
db.init_app(app)

# Registering Blueprints
app.register_blueprint(authenticate, url_prefix='/authenticate')
app.register_blueprint(general, url_prefix='')
app.register_blueprint(users, url_prefix='/user')
app.register_blueprint(quiz_functionality, url_prefix='/quiz')


# Function to enable foreign keys
def enable_foreign_keys(db_conn, connection_record):
    cursor = db_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


with app.app_context():
    # Attach the event listener
    listen(db.engine, 'connect', enable_foreign_keys)
    db.create_all()


if __name__ == "__main__":
    app.run(debug=False, port=5001)


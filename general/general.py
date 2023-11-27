from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user

general = Blueprint("general", __name__, template_folder="templates", static_folder="static",
                    static_url_path='assets')


@general.route('/')
def home():
    return render_template("general/index.html", current_user=current_user)

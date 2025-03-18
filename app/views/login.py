from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import User
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user
from app.decorators import login_required

login_bp = Blueprint("login", __name__)

@login_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))
    return render_template('login.html')

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home.home"))
        flash("Invalid Credentials", "error")
        return render_template("login.html")
    return render_template("login.html")

@login_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login.index"))
from flask import Blueprint, render_template

from app.decorators import login_required

contact_bp = Blueprint("contact_us", __name__)

def calculate_percentage_score(problem_count, total_count):
    if total_count == 0:
        return "N/A"
    score = (1 - (problem_count / total_count)) * 100
    return f"{round(score, 1)}%"

@contact_bp.route("/contact_us")
@login_required
def contact_us():
    return render_template("contact_us.html")
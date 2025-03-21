from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
import json
import os
from flask_login import current_user
from app.decorators import login_required
import pandas as pd
import requests

home_bp = Blueprint("home", __name__)

def calculate_percentage_score(problem_count, total_count):
    if total_count == 0:
        return "N/A"
    score = (1 - (problem_count / total_count)) * 100
    return f"{round(score, 1)}%"

@home_bp.route('/home')
@login_required
def home():
    username = current_user.username
    return render_template('home.html', username=username)


@home_bp.route('/process_json', methods=['POST'])
@login_required
def process_json():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files['file']
        try:
            data = json.load(file)
        except Exception as e:
            return jsonify({"error": "Invalid JSON file."}), 400

        payload = {"query_string": data['analyzeResult']['content']}
        ai_response = requests.post(current_app.config["AZURE_MODEL"], json=payload, headers={"Content-Type": "application/json"})

        data_to_share = []
        sum_total_tokens_count = 0
        sum_total_numbers_count = 0
        sum_lexical_problems = 0
        sum_numerical_problems = 0
        for page in ai_response.json()['page_statistics']:
            sum_total_tokens_count += page['total_tokens_count']
            sum_total_numbers_count += page['total_numbers_count']
            sum_lexical_problems += page['lexical_problem_tokens_count']
            problem_texts = []
            temp_sum_numerical_problems = 0
            for error in page['problems']:
                problem_texts.append(f"{error['error_type'].capitalize()}: {error['explanation']}")
                if error['error_type'] == 'numerical':
                    sum_numerical_problems += 1
                    temp_sum_numerical_problems += 1

            data_to_share.append({
                "Page number": page['page_number'],
                "Lexical score %": calculate_percentage_score(page['lexical_problem_tokens_count'], page['total_tokens_count']),
                "Numerical score %": calculate_percentage_score(temp_sum_numerical_problems, page['total_numbers_count']),
                "Problems": "<br>".join(problem_texts)
            })

        overall_scores = {
            "lexical_score": calculate_percentage_score(sum_lexical_problems, sum_total_tokens_count),
            "numerical_score": calculate_percentage_score(sum_numerical_problems, sum_total_numbers_count)
        }

        download_folder = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(download_folder, exist_ok=True)

        filename = "analysis.xlsx"
        file_path = os.path.join(download_folder, filename)
        pd.DataFrame.from_dict(data_to_share).sort_values('Page number').to_excel(file_path)

        download_url = url_for('home.download_file', filename=filename)

        return jsonify({
            "structured_data": data_to_share,
            "overall_scores": overall_scores,
            "download_url": download_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@home_bp.route('/download/<filename>')
@login_required
def download_file(filename):
    download_folder = os.path.join(os.getcwd(), 'downloads')
    return send_file(os.path.join(download_folder, filename), as_attachment=True)



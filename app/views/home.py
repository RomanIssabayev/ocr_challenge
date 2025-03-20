from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
import json
import os
from flask_login import current_user
from app.decorators import login_required
import pandas as pd
import requests

home_bp = Blueprint("home", __name__)

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
        score_lexical = 0
        score_numerical = 0
        for page in ai_response.json()['page_statistics']:
            data_to_share.append({
                "page_number": page['page_number'],
                "total_tokens_count": page['total_tokens_count'],
                "total_numbers_count": page['total_numbers_count'],
                "lexical_problem_tokens_count": page['lexical_problem_tokens_count'],
                "numerical_problem_tokens_count": page['numerical_problem_tokens_count'],
                "problems": len(page['problems'])
            })
            for error in page['problems']:
                if error['error_type'] == 'lexical':
                    score_lexical += IMPACT_SCORES[classify_error(error['explanation'], error['error_type'])]
                else:
                    score_numerical += IMPACT_SCORES[classify_error(error['explanation'], error['error_type'])]

        download_folder = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(download_folder, exist_ok=True)

        filename = "analysis.xlsx"
        file_path = os.path.join(download_folder, filename)
        pd.DataFrame.from_dict(data_to_share).sort_values('page_number').to_excel(file_path)

        download_url = url_for('home.download_file', filename=filename)

        pivot = [{
            "Lexical mistake score": score_lexical,
            "Numerical mistake score": score_numerical,
        }]

        return jsonify({
            "structured_data": pivot,
            "download_url": download_url
        })

    except Exception as e:
        return jsonify({"error": e}), 400


@home_bp.route('/download/<filename>')
@login_required
def download_file(filename):
    download_folder = os.path.join(os.getcwd(), 'downloads')
    return send_file(os.path.join(download_folder, filename), as_attachment=True)



LEXICAL_ISSUES = {
    "misspelling": ["misspelling", "misspell", "incorrect term", "intended to be"],
    "unclear_abbreviation": ["unclear", "may be an OCR error", "missing context"],
    "incorrect_symbol": ["symbol seems out of place", "incorrect formatting"],
    "hyphenation_issue": ["hyphen split", "incorrect hyphen"],
    "incomplete_word": ["appears incomplete", "incomplete term"],
    "formatting_issue": ["incorrectly formatted", "split word", "hyphenated"],
    "typographical_error": ["typographical error", "does not fit the context"],
    "unusual_term": ["seems unusual", "might be incorrect"]
}

NUMERICAL_ISSUES = {
    "formatting_issue": ["unnecessary space", "formatting", "formatted"],
    "wrong_number": ["incorrect number", "incorrectly written"],
    "consistency_issue": ["should follow the same standard"],
    "unclear_reference": ["appears to be an unexplained numerical reference"],
    "alphanumeric_confusion": ["appears to be a numerical or alphanumeric sequence"],
}

# Assign impact scores to issue categories
IMPACT_SCORES = {
    "misspelling": 2,
    "unclear_abbreviation": 2,
    "incorrect_symbol": 1,
    "hyphenation_issue": 1,
    "incomplete_word": 2,
    "formatting_issue": 1,
    "typographical_error": 1,
    "unusual_term": 2,
    "wrong_number": 5,
    "consistency_issue": 2,
    "unknown": 1,
    "unclear_reference": 2,
    "alphanumeric_confusion": 3,
}

# Function to classify error based on explanation
def classify_error(explanation, error_type):
    if error_type == "lexical":
        for issue, keywords in LEXICAL_ISSUES.items():
            if any(keyword in explanation.lower() for keyword in keywords):
                return issue
    elif error_type == "numerical":
        for issue, keywords in NUMERICAL_ISSUES.items():
            if any(keyword in explanation.lower() for keyword in keywords):
                return issue
    return "unknown"
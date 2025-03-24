from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
import json
import os
from flask_login import current_user
from app.decorators import login_required
import pandas as pd
import requests
import pickle

home_bp = Blueprint("home", __name__)

def calculate_percentage_score(problem_count, total_count):
    if total_count == 0:
        return "N/A"
    score = (1 - (problem_count / total_count)) * 100
    return f"{round(score, 1)}%"

@home_bp.route("/home")
@login_required
def home():
    return render_template("home.html")


@home_bp.route("/process_json", methods=["POST"])
@login_required
def process_json():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files["file"]
        try:
            data = json.load(file)
        except Exception as e:
            return jsonify({"error": f"Invalid JSON file."}), 400


        payload = {"query_string": data["analyzeResult"]["content"]}
        ai_response = requests.post(
            current_app.config["AZURE_MODEL"],
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=600
        )

        data_to_share = []
        for page in ai_response.json()["page_statistics"]:
            problem_texts = []
            data_to_save_in_file = []
            for index,error in enumerate(page["problems"]):
                temp_dict = {
                    "Error #": index + 1,
                    "Type": error["error_type"].capitalize(),
                    "Text": error["problem_text"],
                    "Explanation": error["explanation"]
                }
                problem_texts.append(temp_dict)

                data_to_save_in_file.append({
                    "Page number": page["page_number"],
                    "Lexical score %": page['lexical_score'],
                    "Numerical score %": page['numerical_score'],
                    "Error": index + 1,
                    "Type": error["error_type"].capitalize(),
                    "Text": error["problem_text"],
                    "Explanation": error["explanation"]
                })

            data_to_share.append({
                "Page number": page["page_number"],
                "Lexical score %": page['lexical_score'],
                "Numerical score %": page['numerical_score'],
                "Problems": pd.DataFrame(problem_texts).to_html(index=False)
            })

        overall_scores = {
            "lexical_score": ai_response.json()['overall_lexical_score'],
            "numerical_score": ai_response.json()['overall_numerical_score']
        }

        download_folder = os.path.join(os.getcwd(), "downloads")
        os.makedirs(download_folder, exist_ok=True)

        filename = "analysis.xlsx"
        file_path = os.path.join(download_folder, filename)
        pd.DataFrame.from_dict(data_to_save_in_file).sort_values(["Page number", "Error"]).to_excel(file_path, index=False)

        download_url = url_for("home.download_file", filename=filename)

        return jsonify({
            "structured_data": data_to_share,
            "overall_scores": overall_scores,
            "download_url": download_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@home_bp.route("/download/<filename>")
@login_required
def download_file(filename):
    download_folder = os.path.join(os.getcwd(), "downloads")
    return send_file(os.path.join(download_folder, filename), as_attachment=True)



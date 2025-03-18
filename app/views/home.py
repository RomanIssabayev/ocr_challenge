from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
import json
import os
from flask_login import current_user
from app.decorators import login_required
import pandas as pd
import time

home_bp = Blueprint("home", __name__)

@home_bp.route('/home')
@login_required
def home():
    username = current_user.username
    return render_template('home.html', username=username)


@home_bp.route('/process_json', methods=['POST'])
@login_required
def process_json():
    # Check if a file is provided in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    try:
        data = json.load(file)
    except Exception as e:
        return jsonify({"error": "Invalid JSON file."}), 400

    # Ensure the 'downloads' directory exists.
    download_folder = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(download_folder, exist_ok=True)

    filename = "test_sample.xlsx"
    file_path = os.path.join(download_folder, filename)
    pd.DataFrame.from_dict(data).to_excel(file_path)

    # Create a download URL for the file.
    download_url = url_for('home.download_file', filename=filename)

    # Return both the structured JSON for building a table and the download URL.
    return jsonify({
        "structured_data": data,
        "download_url": download_url
    })


@home_bp.route('/download/<filename>')
@login_required
def download_file(filename):
    download_folder = os.path.join(os.getcwd(), 'downloads')
    return send_file(os.path.join(download_folder, filename), as_attachment=True)
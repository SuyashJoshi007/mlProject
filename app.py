import pickle
from flask import Flask, request, render_template, flash
import numpy as np
import pandas as pd
from src.pipeline.predict_pipeline import CustomData, PredictPipeline
from sklearn.preprocessing import StandardScaler

application = Flask(__name__)
app = application
app.secret_key = "replace_me_with_a_secret"  # needed for flash()

def _get_float(form, name, lo=0, hi=100):
    """Parse float from form[name]; return None if empty/invalid/out-of-range."""
    raw = (form.get(name) or "").strip()
    if raw == "":
        return None
    try:
        val = float(raw)
    except ValueError:
        return None
    return val if lo <= val <= hi else None

def _is_empty(form, name):
    return (form.get(name) or "").strip() == ""

@app.route('/')
def index():
    # Landing page (your marketing/hero page)
    return render_template('index.html')

@app.route('/predictdata', methods=['GET', 'POST'])
def predict_datapoint():
    if request.method == 'GET':
        # Show the form
        return render_template('home.html')

    # -------- POST: validate inputs --------
    f = request.form
    errors = []

    # Required selects
    if _is_empty(f, 'gender'): errors.append("Please select Gender.")
    if _is_empty(f, 'ethnicity'): errors.append("Please select Ethnicity.")
    if _is_empty(f, 'parental_level_of_education'): errors.append("Please select Parent's Education.")
    if _is_empty(f, 'lunch'): errors.append("Please select Lunch type.")
    if _is_empty(f, 'test_preparation_course'): errors.append("Please select Test Preparation.")

    # Numeric fields
    reading = _get_float(f, 'reading_score', 0, 100)
    writing = _get_float(f, 'writing_score', 0, 100)
    if reading is None: errors.append("Reading score must be a number between 0 and 100.")
    if writing is None: errors.append("Writing score must be a number between 0 and 100.")

    # If any errors, show the form again with messages + previously entered values
    if errors:
        flash("Please fill the form correctly.", "error")
        # Pass back the same field values so the form stays filled-in
        return render_template('home.html', errors=errors, form_values=f), 400

    # -------- Build CustomData (FIXED: no swap) --------
    try:
        data = CustomData(
            gender=f.get('gender'),
            race_ethnicity=f.get('ethnicity'),
            parental_level_of_education=f.get('parental_level_of_education'),
            lunch=f.get('lunch'),
            test_preparation_course=f.get('test_preparation_course'),
            reading_score=reading,   # <-- correct
            writing_score=writing    # <-- correct
        )
        pred_df = data.get_data_as_data_frame()
    except Exception as e:
        flash("Internal error preparing data. Please try again.", "error")
        return render_template('home.html', form_values=f), 500

    # -------- Predict --------
    try:
        predict_pipeline = PredictPipeline()
        results = predict_pipeline.predict(pred_df)   # expect array-like
        overall = float(np.squeeze(results))          # ensure scalar
    except Exception as e:
        flash("Prediction failed. Please try again.", "error")
        return render_template('home.html', form_values=f), 500

    # For your result charts, we’ll send:
    # overall, reading, writing, math (use overall for math unless you have a separate math model)
    math = overall

    # -------- Render the results page WITH CHARTS --------
    return render_template(
        'result.html',
        overall=round(overall, 2),
        reading=round(reading, 2),
        writing=round(writing, 2),
        math=round(math, 2),
        gender=f.get('gender'),
        ethnicity=f.get('ethnicity'),
        parental_level_of_education=f.get('parental_level_of_education'),
        lunch=f.get('lunch'),
        test_preparation_course=f.get('test_preparation_course'),
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

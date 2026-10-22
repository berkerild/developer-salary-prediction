"""Backend of the salary app: load the saved model and turn a user's profile into a prediction.

The preparation steps are the same as in notebooks/03_modeling.ipynb.
"""
import joblib
import numpy as np
import pandas as pd
import streamlit as st

# Exchange rate used in the Stack Overflow survey (1,000,000 EUR became 1,160,147 USD)
EUR_TO_USD = 1.16

# Typical error of the model on the test set (about 20%)
TYPICAL_ERROR = 0.20

# Natural order of the education levels, as in notebooks 02 and 03
EDLEVEL_ORDER = ["Secondary or lower", "Some college", "Associate", "Bachelor",
                 "Master", "Doctorate/professional"]

# All 42 languages of the survey. The model uses 19 of them as columns,
# but n_languages counts all of them, as in the notebook.
ALL_LANGUAGES = [
    "Ada", "Assembly", "Bash/Shell", "C", "C#", "C++", "COBOL", "Dart", "Delphi", "Elixir",
    "Erlang", "F#", "Fortran", "GDScript", "Gleam", "Go", "Groovy", "HTML/CSS", "Java",
    "JavaScript", "Kotlin", "Lisp", "Lua", "MATLAB", "MicroPython", "Mojo", "OCaml", "PHP",
    "Perl", "PowerShell", "Prolog", "Python", "R", "Ruby", "Rust", "SQL", "Scala", "Swift",
    "TypeScript", "VBA", "Visual Basic", "Zig"]


@st.cache_resource
def load_model():
    """Load the final model and the preprocessing objects once, and keep them in memory."""
    model = joblib.load("models/xgb_final_model.joblib")
    prep = joblib.load("models/preprocessing.joblib")
    return model, prep


def get_options(prep):
    """Lists of choices for the input fields, taken from the training data."""
    encoder = prep["encoder"]
    options = {}
    for col, categories in zip(prep["onehot_cols"], encoder.categories_):
        options[col] = [c for c in categories if c != "unknown"]
    options["EdLevel"] = [level for level in EDLEVEL_ORDER if level in options["EdLevel"]]
    options["OrgSize"] = list(prep["orgsize_map"].keys())
    options["Age"] = list(prep["age_map"].keys())
    options["Languages"] = ALL_LANGUAGES
    return options


def prepare_input(profile, prep):
    """Turn one profile (a dict) into the 88-column table the model expects.

    Fields the user didn't fill in are None and are filled the same way as in the notebook.
    """
    languages = profile["Languages"]
    has_languages = len(languages) > 0

    # Numeric features
    # ----------------
    work_exp = profile["WorkExp"]
    years_code = profile["YearsCode"]
    row = pd.DataFrame({
        "WorkExp_log": [np.log1p(work_exp)],
        "coding_before_work": [years_code - work_exp if years_code is not None else np.nan],
        "n_languages": [len(languages) if has_languages else np.nan],
    })
    row = row.fillna(prep["numeric_medians"])

    # Ordinal features (most frequent value if not given)
    # ---------------------------------------------------
    org_size = profile["OrgSize"] or prep["ordinal_modes"]["OrgSize"]
    age = profile["Age"] or prep["ordinal_modes"]["Age"]
    row["OrgSize_encoded"] = prep["orgsize_map"][org_size]
    row["Age_encoded"] = prep["age_map"][age]

    # Scaling
    # -------
    scaled = pd.DataFrame(prep["scaler"].transform(row), columns=row.columns)

    # One-hot features ("unknown" if not given)
    # -----------------------------------------
    categorical = pd.DataFrame({col: [profile[col] or "unknown"] for col in prep["onehot_cols"]})
    onehot = pd.DataFrame(prep["encoder"].transform(categorical),
                          columns=prep["encoder"].get_feature_names_out(prep["onehot_cols"]))

    # Languages
    # ---------
    lang = pd.DataFrame({"languages_missing": [0 if has_languages else 1]})
    for col in prep["selected_langs"]:
        lang[col] = [1 if col.replace("lang_", "") in languages else 0]

    # Same columns, in the same order as in training
    X = pd.concat([scaled, onehot, lang], axis=1)
    return X[prep["final_columns"]]


def predict_salary(profile, model, prep):
    """Predicted typical annual salary in USD."""
    X = prepare_input(profile, prep)
    return float(np.exp(model.predict(X))[0])

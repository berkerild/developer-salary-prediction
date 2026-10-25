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


@st.cache_data
def load_data():
    """Load the cleaned survey data from notebook 01 (only once)."""
    return pd.read_csv("data/processed/survey_clean_2025.csv")


def country_medians_eur():
    """Median salary per country in EUR, lowest first."""
    df = load_data()
    medians = df.groupby("Country")["ConvertedCompYearly"].median() / EUR_TO_USD
    return medians.sort_values().reset_index(name="median_eur")


EXP_BINS = [-1, 2, 5, 10, 15, 20, 30, 50]
EXP_LABELS = ["0-2", "3-5", "6-10", "11-15", "16-20", "21-30", "31+"]


def experience_medians_eur():
    """Median salary in EUR per experience band."""
    df = load_data().copy()
    df["band"] = pd.cut(df["WorkExp"], EXP_BINS, labels=EXP_LABELS)
    medians = df.groupby("band", observed=True)["ConvertedCompYearly"].median() / EUR_TO_USD
    return medians.reset_index(name="median_eur")


def factor_ratios():
    """How many times the highest group earns more than the lowest, per factor."""
    df = load_data().copy()
    df["Experience"] = pd.cut(df["WorkExp"], EXP_BINS, labels=EXP_LABELS)
    columns = {"Country": "Country", "Experience": "Experience", "DevType": "Role",
               "Industry": "Industry", "RemoteWork": "Way of working", "EdLevel": "Education",
               "OrgSize": "Company size", "ICorPM": "Managing people"}
    rows = []
    for column, label in columns.items():
        medians = df.groupby(column, observed=True)["ConvertedCompYearly"].median()
        rows.append({"factor": label, "ratio": medians.max() / medians.min()})
    rows.append({"factor": "Number of languages", "ratio": 1.0})
    return pd.DataFrame(rows).sort_values("ratio", ascending=False)


def manager_gap_by_experience():
    """Median salary in EUR of managers and individual contributors, per experience band."""
    df = load_data().copy()
    df["band"] = pd.cut(df["WorkExp"], EXP_BINS, labels=EXP_LABELS)
    table = df.pivot_table(index="band", columns="ICorPM", values="ConvertedCompYearly",
                           aggfunc="median", observed=True) / EUR_TO_USD
    table = table.reset_index().melt(id_vars="band", var_name="role", value_name="median_eur")
    return table.dropna()


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


# ---------------------------------------------------------------
# Added for pages 4, 5 and 6
# ---------------------------------------------------------------

# The offer from page 1, so pages 5 and 6 use the same profile
DEMO_OFFER = 55_000  # EUR a year
DEMO_PROFILE = {
    "Country": "Netherlands", "WorkExp": 5, "DevType": "Back-end developer",
    "ICorPM": "Individual contributor", "EdLevel": None, "OrgSize": None,
    "RemoteWork": None, "Industry": None, "Age": None, "YearsCode": None, "Languages": [],
}

# Test set results from notebook 03 (USD), the only time the test set was used
TEST_SIZE = 1_486
TEST_RESULTS = pd.DataFrame({
    "model": ["One median for everyone", "Median of each country", "Final model (XGBoost)"],
    "mae": [31_698, 27_510, 21_462],
    "r2": [-0.03, 0.14, 0.39],
})

# Median percentage error by real salary (USD), test set, notebook 03 "By salary level"
SALARY_BINS = [0, 40_000, 60_000, 80_000, 100_000, 150_000, 500_000]
ERROR_BY_SALARY = pd.DataFrame({
    "band": ["<40k", "40-60k", "60-80k", "80-100k", "100-150k", "150k+"],
    "people": [151, 316, 346, 294, 273, 106],
    "pct_error": [38, 23, 16, 14, 18, 36],
})


# Feature importance of the final model, grouped back to the survey questions
# (notebook 03, "Importance by feature"). Sums to 1.
IMPORTANCE_BY_FEATURE = pd.DataFrame({
    "feature": ["Country", "Languages", "Industry", "Role", "Education",
                "Experience", "Remote work", "Age", "Company size", "Managing people"],
    "importance": [0.476, 0.156, 0.090, 0.082, 0.051, 0.045, 0.036, 0.022, 0.015, 0.011],
})


# Model comparison on the VALIDATION set, after tuning (notebook 03).
# This set, split from the training data, is the one used to choose the model;
# the test set was touched only once, at the very end. Kept separate on purpose.
VALIDATION_RESULTS = pd.DataFrame({
    "model": ["Linear (SGD)", "Random forest", "XGBoost (tuned)"],
    "mae": [22_326, 22_175, 21_155],
})

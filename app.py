"""Developer Salary Check: a small Streamlit app on top of the final model.

Run from the repository folder with:  streamlit run app.py
"""
import streamlit as st
from backend import load_model, get_options, predict_salary, EUR_TO_USD, TYPICAL_ERROR

NOT_SPECIFIED = "Not specified"


def optional(label, choices):
    """Select box with a 'Not specified' option; returns None if nothing was chosen."""
    choice = st.sidebar.selectbox(label, [NOT_SPECIFIED] + choices)
    return None if choice == NOT_SPECIFIED else choice


def main():
    st.title("Developer Salary Check")
    st.write("Is your job offer fair? Fill in your profile on the left to see the typical "
             "annual salary for developers like you in Europe.")

    model, prep = load_model()
    options = get_options(prep)

    # Required fields
    # ---------------
    st.sidebar.header("Your profile")
    country = st.sidebar.selectbox("Country", sorted(options["Country"]))
    work_exp = st.sidebar.slider("Years of professional work experience", 0, 50, 5)
    dev_type = st.sidebar.selectbox("Role", sorted(options["DevType"]))
    manager = st.sidebar.radio("Do you manage people?", ["Individual contributor", "Manager"])

    # Optional fields
    # ---------------
    st.sidebar.header("Optional")
    ed_level = optional("Education", options["EdLevel"])
    org_size = optional("Company size (employees)", options["OrgSize"])
    remote = optional("Way of working", sorted(options["RemoteWork"]))
    industry = optional("Industry", sorted(options["Industry"]))
    age = optional("Age", options["Age"])
    years_code = st.sidebar.number_input("Years of coding, including education", 0, 60,
                                         value=None, placeholder=NOT_SPECIFIED)
    languages = st.sidebar.multiselect("Programming languages used in the past year",
                                       options["Languages"])

    profile = {
        "Country": country, "WorkExp": work_exp, "DevType": dev_type, "ICorPM": manager,
        "EdLevel": ed_level, "OrgSize": org_size, "RemoteWork": remote, "Industry": industry,
        "Age": age, "YearsCode": years_code, "Languages": languages,
    }

    # Currency and offer
    # ------------------
    currency = st.radio("Currency", ["EUR", "USD"], horizontal=True)
    offer = st.number_input(f"Your offer (annual, {currency}, optional)", min_value=0,
                            value=None, step=1000, placeholder="e.g. 60000")

    # Prediction
    # ----------
    salary_usd = predict_salary(profile, model, prep)
    rate = EUR_TO_USD if currency == "EUR" else 1
    salary = salary_usd / rate
    low, high = salary * (1 - TYPICAL_ERROR), salary * (1 + TYPICAL_ERROR)

    st.metric("Typical salary for your profile", f"{salary:,.0f} {currency}")
    st.write(f"Typical range: **{low:,.0f} to {high:,.0f} {currency}** "
             f"(the model is usually within about 20%).")

    if offer:
        if offer < low:
            st.warning(f"Your offer is below the typical range, about {(1 - offer / salary) * 100:.0f}% "
                       "below the typical salary. That's a good reason to negotiate.")
        elif offer > high:
            st.info("Your offer is above the typical range for your profile.")
        else:
            st.success("Your offer is within the typical range for your profile.")

    st.caption("Based on the Stack Overflow Developer Survey 2025 (employed professional developers "
               "in Europe). The model is less reliable for very high or very low salaries and in "
               "Eastern and Southern Europe. "
               + (f"Conversion: 1 EUR = {EUR_TO_USD} USD (rate used in the survey)." if currency == "EUR" else ""))


if __name__ == '__main__':
    main()

import streamlit as st
from style import apply_style

st.set_page_config(page_title="Developer Salary Check", page_icon=":material/payments:", layout="wide")
apply_style()

pg = st.navigation([
    st.Page("pages/1_question.py", title="The question", icon=":material/help:"),
    st.Page("pages/2_drivers.py", title="What drives salary", icon=":material/public:"),
    st.Page("pages/3_is_it_real.py", title="Is it real?", icon=":material/fact_check:"),
    st.Page("pages/4_model.py", title="The model", icon=":material/model_training:"),
    st.Page("pages/5_calculator.py", title="Salary check", icon=":material/calculate:"),
    st.Page("pages/6_what_to_do.py", title="What to do", icon=":material/lightbulb:"),
])
pg.run()

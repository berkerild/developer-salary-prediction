import streamlit as st
from style import section_title

OFFER = 55_000

section_title("Is this job offer fair?")
st.caption("Developer Salary Prediction, by Berker Ildokuz (Ironhack Data Analytics)")

with st.container(key="hero"):
    left, right = st.columns([3, 2], gap="large", vertical_alignment="center")
    with left:
        st.markdown("<div class='hero-small'>A back-end developer in the Netherlands "
                    "with 5 years of experience is offered</div>"
                    f"<div class='offer-amount'>{OFFER:,} EUR a year</div>",
                    unsafe_allow_html=True)
    with right:
        st.markdown("<div class='hero-question'>Is that fair?</div>"
                    "<div class='hero-small' style='margin-top:0.5rem'>Nobody really knows. "
                    "Salaries are rarely discussed openly.</div>", unsafe_allow_html=True)

st.write("")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Tech specialists in the EU", "10.45M", "+59% in ten years", border=True)
c2.metric("Tech job postings", "Below 2020", "-18% worldwide", delta_color="inverse", border=True)
c3.metric("Work fully remote", "1 in 4", "comparing offers across borders", delta_color="off", border=True)
c4.metric("Gap between countries", "3x", "for the same job", delta_color="off", border=True)
st.caption("Sources: Eurostat and Indeed Hiring Lab (market), Stack Overflow Developer Survey 2025 "
           "(remote work and country gap)")

st.write("")

with st.container(border=True):
    st.subheader("How I answer it")

    steps = [
        ("What drives salary?", "Country and experience matter most."),
        ("Are the differences real?", "Six statistical tests."),
        ("A model that predicts it", "22% less error than knowing only the country."),
        ("Check the offer", "A live salary check for this developer."),
    ]

    for number, (col, (title, text)) in enumerate(zip(st.columns(4, gap="medium"), steps), start=1):
        col.markdown(f"<div class='step-card'><div class='step-num'>{number}</div>"
                     f"<div class='step-title'>{title}</div>"
                     f"<div class='step-text'>{text}</div></div>", unsafe_allow_html=True)

st.write("")
st.caption("Goal: a data-based reference for developer salaries, built on 7,428 professional "
           "developers in 31 European countries.")

import streamlit as st
from backend import (load_model, predict_salary, country_medians_eur, EUR_TO_USD, TYPICAL_ERROR,
                     DEMO_OFFER, DEMO_PROFILE)
from style import section_title

section_title("What can you do with this?")
st.caption("Back to the offer from page 1, and three things any developer can use")

model, prep = load_model()
typical = predict_salary(DEMO_PROFILE, model, prep) / EUR_TO_USD
low, high = typical * (1 - TYPICAL_ERROR), typical * (1 + TYPICAL_ERROR)
gap = DEMO_OFFER / typical - 1

medians = country_medians_eur()
country_median = medians.loc[medians["Country"] == DEMO_PROFILE["Country"], "median_eur"].iloc[0]

GOLD = "#D9A400"
GREEN = "#3E7C6B"
BLUE_LIGHT = "#5B82D9"

if DEMO_OFFER < low:
    verdict = "Below the typical range"
    advice = f"{-gap:.0%} below the typical salary for this profile: a good reason to negotiate."
    stripe = GOLD
elif DEMO_OFFER > high:
    verdict = "Above the typical range"
    advice = f"{gap:.0%} above the typical salary for this profile: a strong offer."
    stripe = BLUE_LIGHT
else:
    verdict = "Within the typical range"
    advice = f"{gap:+.0%} compared with the typical salary for this profile: a fair offer."
    stripe = GREEN

with st.container(key="verdict"):
    st.markdown(f"<style>.st-key-verdict{{border-left-color:{stripe};}}</style>",
                unsafe_allow_html=True)
    left, right = st.columns([3, 2], gap="large", vertical_alignment="center")
    with left:
        st.markdown("<div class='verdict-sub' style='margin-top:0'>The 55,000 EUR offer from "
                    "page 1 is</div>"
                    f"<div class='verdict-big'>{verdict}</div>"
                    f"<div class='verdict-sub'>{advice}</div>", unsafe_allow_html=True)
    with right:
        st.markdown(f"<div class='verdict-amount-label'>Typical salary for this profile</div>"
                    f"<div class='verdict-amount'>{typical:,.0f} EUR</div>"
                    f"<div class='verdict-amount-label'>range {low:,.0f} to {high:,.0f} · "
                    f"NL median {country_median:,.0f}</div>", unsafe_allow_html=True)

st.write("")

st.subheader("For any developer with an offer")

steps = [
    ("Compare within your country", "Country moves salary most, so comparing across borders "
     "is misleading."),
    ("Use the prediction as a range", f"The typical error is about {TYPICAL_ERROR:.0%}. More than "
     f"{TYPICAL_ERROR:.0%} below the prediction: a good reason to negotiate."),
    ("Which languages, not how many", "The number of languages has no relation with salary; "
     "back-end and infrastructure languages go with higher pay."),
]

for col, (title, text) in zip(st.columns(3, gap="large"), steps):
    col.markdown(f"<div class='rec-card'><div class='rec-title'>{title}</div>"
                 f"<div class='rec-text'>{text}</div></div>", unsafe_allow_html=True)

st.write("")
st.write("")

f1, f2 = st.columns(2, gap="large")
f1.markdown("<div class='finding'><div class='finding-title'>Use it with care</div>"
            "<div class='finding-text'>Only for employed developers in Europe. Self-reported "
            "survey data, converted to USD, without cost of living. The model explains 39% of "
            "the differences: the company, the city and negotiation skills are not in the data."
            "</div></div>", unsafe_allow_html=True)
f2.markdown("<div class='finding'><div class='finding-title'>Next steps</div>"
            "<div class='finding-text'>Publish the app online. A range per country instead of a "
            "fixed 20% (9% in Finland, 26% in Poland). More currencies, and earlier survey years "
            "for small countries.</div></div>", unsafe_allow_html=True)

st.write("")
st.divider()
st.caption("Developer Salary Prediction · Berker Ildokuz · Ironhack Data Analytics. "
           "Thank you for your attention.")

import altair as alt
import pandas as pd
import streamlit as st
from backend import (TEST_RESULTS, TEST_SIZE, TYPICAL_ERROR, IMPORTANCE_BY_FEATURE,
                     VALIDATION_RESULTS)
from style import tidy, section_title

GOLD = "#D9A400"
BLUE = "#1D3F8F"
GREY = "#9AA4B5"


section_title("How good is the model?")
st.caption(f"XGBoost on log salary, tested once on {TEST_SIZE:,} developers it had never seen. "
           "Errors in USD, as in the survey and notebook 03.")

final = TEST_RESULTS.iloc[2]
country_only = TEST_RESULTS.iloc[1]
improvement = 1 - final["mae"] / country_only["mae"]

c1, c2, c3 = st.columns(3)
c1.metric("Average error (MAE)", f"{final['mae']:,.0f} USD",
          f"-{improvement:.0%} vs country only", delta_color="inverse", border=True)
c2.metric("Typical error, in % of the real salary", f"about {TYPICAL_ERROR:.0%}", border=True)
c3.metric("Salary differences explained (R²)", f"{final['r2']:.0%}", border=True)

st.write("")

left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.markdown("<div style='font-weight:600;font-size:1.05rem;margin-bottom:0.6rem'>"
                    "Better than knowing only the country</div>", unsafe_allow_html=True)

        results = TEST_RESULTS.copy()
        results["final"] = results["model"].str.startswith("Final")
        results["label"] = results["mae"].apply(lambda v: f"{v:,.0f} USD")

        order = results["model"].tolist()
        base = alt.Chart(results).encode(y=alt.Y("model:N", sort=order, title=None, axis=None))
        bars = base.mark_bar(height=26, cornerRadiusEnd=3).encode(
            x=alt.X("mae:Q", title=None, scale=alt.Scale(domain=[0, 40_000]), axis=None),
            color=alt.condition("datum.final", alt.value(BLUE), alt.value(GREY)),
            tooltip=[alt.Tooltip("model:N", title="Model"),
                     alt.Tooltip("label:N", title="Average error")],
        )
        names = base.mark_text(align="left", dx=2, dy=-22, fontSize=14, fontWeight=500,
                               color="#3A4459").encode(x=alt.datum(0), text="model:N")
        values = base.mark_text(align="left", dx=7, fontSize=13, fontWeight=600,
                                color="#3A4459").encode(x="mae:Q", text="label:N")

        st.altair_chart(tidy((bars + names + values).properties(height=320)),
                        use_container_width=True)
        st.caption("Average error on the test set. Lower is better.")

with right:
    with st.container(border=True):
        st.markdown("<div style='font-weight:600;font-size:1.05rem;margin-bottom:0.6rem'>"
                    "What the model relies on</div>", unsafe_allow_html=True)

        imp = IMPORTANCE_BY_FEATURE.copy()
        imp["top"] = imp["feature"] == "Country"
        imp["label"] = (imp["importance"] * 100).round(0).astype(int).astype(str) + "%"

        order = imp["feature"].tolist()
        base = alt.Chart(imp).encode(
            y=alt.Y("feature:N", sort=order, title=None,
                    axis=alt.Axis(labelFontSize=13, labelColor="#3A4459", labelPadding=8,
                                  ticks=False, domain=False)))
        bars = base.mark_bar(height=20, cornerRadiusEnd=3).encode(
            x=alt.X("importance:Q", title=None, scale=alt.Scale(domain=[0, 0.58]), axis=None),
            color=alt.condition("datum.top", alt.value(BLUE), alt.value(GREY)),
            tooltip=[alt.Tooltip("feature:N", title="Feature"),
                     alt.Tooltip("label:N", title="Importance")],
        )
        values = base.mark_text(align="left", dx=6, fontSize=13, fontWeight=600,
                                color="#3A4459").encode(x="importance:Q", text="label:N")

        st.altair_chart(tidy((bars + values).properties(height=320)),
                        use_container_width=True)
        st.caption("Country alone is about half. This is the EDA finding, "
                   "seen from inside the model.")

st.write("")

with st.container(border=True):
    st.markdown("<div style='font-weight:600;font-size:1.05rem;margin-bottom:0.6rem'>"
                "The models I compared, before choosing one</div>", unsafe_allow_html=True)

    val = VALIDATION_RESULTS.copy()
    val["best"] = val["model"].str.startswith("XGBoost")
    val["label"] = val["mae"].apply(lambda v: f"{v:,.0f} USD")

    order = val["model"].tolist()
    base = alt.Chart(val).encode(
        y=alt.Y("model:N", sort=order, title=None,
                axis=alt.Axis(labelFontSize=13, labelColor="#3A4459", labelPadding=10,
                              labelLimit=200, ticks=False, domain=False)))
    bars = base.mark_bar(height=26, cornerRadiusEnd=3).encode(
        x=alt.X("mae:Q", title=None, scale=alt.Scale(domain=[0, 26_000]), axis=None),
        color=alt.condition("datum.best", alt.value(GOLD), alt.value(GREY)),
        tooltip=[alt.Tooltip("model:N", title="Model"),
                 alt.Tooltip("label:N", title="Average error")],
    )
    values = base.mark_text(align="left", dx=7, fontSize=13, fontWeight=600,
                            color="#3A4459").encode(x="mae:Q", text="label:N")
    st.altair_chart(tidy((bars + values).properties(height=180)),
                    use_container_width=True)
    st.caption("Average error on the validation set, used only for choosing the model. "
               "Three models were almost tied; tuning made XGBoost the winner. "
               "The test set above was kept untouched until the end.")

st.write("")

f1, f2 = st.columns(2, gap="large")
f1.markdown("<div class='finding'><div class='finding-title'>It explains 39% of the "
            "differences</div><div class='finding-text'>I compared four models and picked the "
            "best. The rest comes from things not in the survey: the company, the city and "
            "negotiation skills.</div></div>", unsafe_allow_html=True)
f2.markdown("<div class='finding'><div class='finding-title'>It predicts the typical salary, "
            "not yours</div><div class='finding-text'>Country is half of what the model uses. "
            "It pulls predictions toward the middle, so very high salaries come out too low "
            "and very low ones too high.</div></div>", unsafe_allow_html=True)

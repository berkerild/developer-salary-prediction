import altair as alt
import streamlit as st
from backend import factor_ratios, experience_medians_eur
from style import tidy, section_title

GOLD = "#D9A400"
BLUE = "#1D3F8F"
GREY = "#9AA4B5"

EXP_ORDER = ["0-2", "3-5", "6-10", "11-15", "16-20", "21-30", "31+"]


section_title("What drives a developer’s salary?")
st.caption("Highest vs lowest group, median salary, 7,428 developers in Europe")

left, right = st.columns([3, 2], gap="large")

with left:
    with st.container(border=True):
        ratios = factor_ratios()
        ratios["top_two"] = ratios["factor"].isin(["Country", "Experience"])
        ratios["label"] = ratios["ratio"].apply(lambda r: "no relation" if r == 1 else f"{r:.1f}x")

        order = ratios["factor"].tolist()
        base = alt.Chart(ratios).encode(
            y=alt.Y("factor:N", sort=order, title=None,
                    axis=alt.Axis(labelFontSize=13, labelColor="#3A4459", labelPadding=8,
                                  labelLimit=200, ticks=False, domain=False)))
        bars = base.mark_bar(height=22, cornerRadiusEnd=3).encode(
            x=alt.X("ratio:Q", title=None, scale=alt.Scale(domain=[0, 3.5]), axis=None),
            color=alt.condition("datum.top_two", alt.value(BLUE), alt.value(GREY)),
            tooltip=[alt.Tooltip("factor:N", title="Factor"),
                     alt.Tooltip("label:N", title="Difference")],
        )
        values = base.mark_text(align="left", dx=6, fontSize=13, fontWeight=600,
                                color="#3A4459").encode(x="ratio:Q", text="label:N")

        st.altair_chart(tidy((bars + values).properties(height=420)),
                        use_container_width=True)
        st.caption("Each bar: how many times more the highest group earns than the lowest.")

with right:
    with st.container(border=True):
        st.markdown("<div style='font-weight:600;font-size:1.05rem;margin-bottom:0.3rem'>"
                    "Experience pays off early, then flattens</div>", unsafe_allow_html=True)

        exp = experience_medians_eur()
        line = alt.Chart(exp).mark_line(color=BLUE, strokeWidth=3, point=alt.OverlayMarkDef(
            color=BLUE, size=70)).encode(
            x=alt.X("band:N", title="Years of professional experience",
                    sort=EXP_ORDER, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("median_eur:Q", title="Median salary (EUR)",
                    scale=alt.Scale(domain=[30_000, 90_000]), axis=alt.Axis(format=",.0f")),
            tooltip=[alt.Tooltip("band:N", title="Experience"),
                     alt.Tooltip("median_eur:Q", title="Median (EUR)", format=",.0f")],
        )
        marker = alt.Chart(exp[exp["band"] == "3-5"]).mark_point(
            size=320, color=GOLD, strokeWidth=3, shape="circle").encode(
            x=alt.X("band:N", sort=EXP_ORDER), y="median_eur:Q")

        st.altair_chart(tidy((line + marker).properties(height=330)),
                        use_container_width=True)
        st.caption("The developer from the offer, with 5 years, is in the gold point.")

st.write("")

f1, f2 = st.columns(2, gap="large")
f1.markdown("<div class='finding'><div class='finding-title'>Country moves the salary most</div>"
            "<div class='finding-text'>The median developer earns 123,000 EUR in Switzerland and "
            "40,000 EUR in Greece. The Netherlands sits in the middle, at 70,000 EUR.</div></div>",
            unsafe_allow_html=True)
f2.markdown("<div class='finding'><div class='finding-title'>How many languages you know "
            "doesn’t matter</div><div class='finding-text'>But which ones does: Ruby +23%, "
            "Go +12%, while PHP users earn 17% less.</div></div>", unsafe_allow_html=True)

import altair as alt
import streamlit as st
from backend import manager_gap_by_experience
from style import tidy, section_title

GOLD = "#D9A400"
BLUE = "#1D3F8F"
GREY = "#9AA4B5"

EXP_ORDER = ["0-2", "3-5", "6-10", "11-15", "16-20", "21-30", "31+"]


def tidy_axis(chart):
    """Shared axis styling, so every chart on every page looks the same."""
    return chart.configure_axis(
        labelFontSize=12, titleFontSize=12, labelColor="#3A4459", titleColor="#5B6475",
        grid=False, domainColor="#D9DEE7", tickColor="#D9DEE7",
        labelFont="IBM Plex Sans", titleFont="IBM Plex Sans")


section_title("Are these differences real?")
st.caption("Six statistical tests on 7,428 developers, significance level 0.05")

left, right = st.columns([2, 3], gap="large")

with left:
    with st.container(border=True):
        tests = [
            ("Do managers earn more?", "Yes, +20%"),
            ("Does the way of working matter?", "Yes, +39%"),
            ("Does education matter?", "Yes, +37%"),
            ("Does experience go with salary?", "Yes, r = 0.45"),
            ("Are managers older?", "Yes"),
            ("Are salaries normally distributed?", "No, but log salaries are"),
        ]
        for question, answer in tests:
            st.markdown(f"<div class='test-row'><div class='test-q'>{question}</div>"
                        f"<div class='test-a'><span class='test-yes'>{answer}</span> "
                        f"&nbsp;·&nbsp; p &lt; 0.05</div></div>", unsafe_allow_html=True)
        st.caption("All six were significant. With 7,400 rows almost everything is, "
                   "so the size of the difference matters more than the p-value.")

with right:
    with st.container(border=True):
        st.markdown("<div style='font-weight:600;font-size:1.05rem;margin-bottom:0.3rem'>"
                    "But significant does not mean important</div>", unsafe_allow_html=True)

        gap = manager_gap_by_experience()
        chart = alt.Chart(gap).mark_line(strokeWidth=3, point=alt.OverlayMarkDef(size=60)).encode(
            x=alt.X("band:N", title="Years of professional experience",
                    sort=EXP_ORDER, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("median_eur:Q", title="Median salary (EUR)",
                    scale=alt.Scale(domain=[30_000, 95_000]), axis=alt.Axis(format=",.0f")),
            color=alt.Color("role:N", title=None,
                            scale=alt.Scale(domain=["Manager", "Individual contributor"],
                                            range=[GOLD, BLUE]),
                            legend=alt.Legend(orient="bottom-right", labelFontSize=12)),
            tooltip=[alt.Tooltip("role:N", title="Role"),
                     alt.Tooltip("band:N", title="Experience"),
                     alt.Tooltip("median_eur:Q", title="Median (EUR)", format=",.0f")],
        )
        st.altair_chart(tidy_axis(chart.properties(height=330)), use_container_width=True)
        st.caption("Managers (gold) always earn more, but the gap shrinks at the same experience.")

st.write("")

f1, f2 = st.columns(2, gap="large")
f1.markdown("<div class='finding'><div class='finding-title'>Half of the manager gap is "
            "experience</div><div class='finding-text'>Managers earn 20% more, but they also "
            "have five more years of experience. At the same experience, the gap is about 9%."
            "</div></div>", unsafe_allow_html=True)
f2.markdown("<div class='finding'><div class='finding-title'>Remote work is not just a country "
            "effect</div><div class='finding-text'>Fully remote developers earn 39% more than "
            "in-person ones. Within Germany alone, the gap is still 33%.</div></div>",
            unsafe_allow_html=True)

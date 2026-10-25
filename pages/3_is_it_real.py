import altair as alt
import streamlit as st
from backend import manager_gap_by_experience, manager_overall_eur
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
        hold = st.toggle("Compare at the same experience", value=False)

        if not hold:
            # Raw view: one gap for everyone -> looks big
            st.markdown("<div style='font-weight:600;font-size:1.05rem;margin-bottom:0.3rem'>"
                        "Managers earn about 20% more</div>", unsafe_allow_html=True)

            overall = manager_overall_eur()
            overall["label"] = overall["median_eur"].apply(lambda v: f"{v:,.0f} EUR")
            role_order = ["Manager", "Individual contributor"]
            base = alt.Chart(overall).encode(
                y=alt.Y("role:N", sort=role_order, title=None,
                        axis=alt.Axis(labelFontSize=13, labelColor="#3A4459", labelPadding=10,
                                      labelLimit=220, ticks=False, domain=False)))
            bars = base.mark_bar(height=48, cornerRadiusEnd=3).encode(
                x=alt.X("median_eur:Q", title=None, scale=alt.Scale(domain=[0, 95_000]),
                        axis=None),
                color=alt.Color("role:N", sort=role_order,
                                scale=alt.Scale(domain=role_order, range=[GOLD, BLUE]),
                                legend=None),
                tooltip=[alt.Tooltip("role:N", title="Role"),
                         alt.Tooltip("label:N", title="Median (EUR)")],
            )
            values = base.mark_text(align="left", dx=7, fontSize=14, fontWeight=600,
                                    color="#3A4459").encode(x="median_eur:Q", text="label:N")
            st.altair_chart(tidy_axis((bars + values).properties(height=330)
                                      .configure_view(stroke=None)), use_container_width=True)
            st.caption("Overall median salary. Looks like a clear 20% manager premium. "
                       "Turn on the switch above to hold experience constant.")
        else:
            # Controlled view: same experience -> the gap shrinks
            st.markdown("<div style='font-weight:600;font-size:1.05rem;margin-bottom:0.3rem'>"
                        "At the same experience, the gap shrinks to about 9%</div>",
                        unsafe_allow_html=True)

            gap = manager_gap_by_experience()
            chart = alt.Chart(gap).mark_line(
                strokeWidth=3, point=alt.OverlayMarkDef(size=60)).encode(
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
            st.caption("At each experience level the two lines sit close together. "
                       "Half of the manager premium was really just experience.")

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

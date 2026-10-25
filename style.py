import streamlit as st

# Colours used in the custom CSS (the rest comes from .streamlit/config.toml)
GOLD = "#D9A400"
GOLD_LIGHT = "#F2C230"
NAVY = "#14213D"
BLUE_DARK = "#1D3F8F"
MUTED = "#5B6475"


def apply_style():
    """Small CSS additions on top of the theme: offer card, metric labels, title."""
    st.markdown(f"""
    <style>
    /* Wide layout, but not wider than 1200px so lines stay readable */
    [data-testid="stMainBlockContainer"], .block-container {{ max-width: 1200px; }}

    /* Page title: a bit tighter, and less space above it */
    h1 {{ letter-spacing: -0.02em; }}
    [data-testid="stMainBlockContainer"] {{ padding-top: 2.5rem; padding-bottom: 2rem; }}

    /* Test result rows on page 3 */
    .test-row {{ padding: 0.55rem 0 0.5rem 0; border-top: 1px solid #E2E6ED; }}
    .test-row .test-q {{ font-weight: 600; font-size: 1rem; }}
    .test-row .test-a {{ color: {MUTED}; font-size: 0.9rem; }}
    .test-yes {{ color: {BLUE_DARK}; font-weight: 600; }}

    /* Highlight box used for a key finding */
    .finding {{
        border-left: 5px solid {GOLD};
        background: #FFFFFF;
        padding: 0.9rem 1.2rem;
        border-radius: 4px;
    }}
    .finding .finding-title {{ font-weight: 600; font-size: 1.05rem; }}
    .finding .finding-text {{ color: {MUTED}; font-size: 0.92rem; line-height: 1.4; }}

    /* A quiet card used for the steps on page 1 */
    .step-card {{
        border-top: 3px solid {GOLD};
        padding-top: 0.6rem;
    }}
    .step-card .step-title {{ font-weight: 600; font-size: 1rem; }}
    .step-card .step-text {{ color: {MUTED}; font-size: 0.9rem; line-height: 1.35; }}

    /* Metric labels in a muted colour, so the numbers stand out */
    [data-testid="stMetricLabel"] p {{ color: {MUTED}; font-size: 0.95rem; }}

    /* The offer card on page 1 (st.container with key="offer") */
    .st-key-offer {{
        background: #FFFFFF;
        border-left: 6px solid {GOLD};
        border-radius: 4px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 2px rgba(20, 33, 61, 0.08);
    }}
    .st-key-offer h2 {{ font-size: 2.6rem; padding: 0.2rem 0; }}

    /* Hero card on page 1 (st.container with key="hero") */
    .st-key-hero {{
        background: {NAVY};
        border-radius: 6px;
        padding: 1.6rem 2rem;
    }}
    .st-key-hero p, .st-key-hero h1, .st-key-hero h2, .st-key-hero h3 {{ color: #FFFFFF; }}
    .st-key-hero .offer-amount {{
        color: {GOLD_LIGHT}; font-size: 3.6rem; font-weight: 600; line-height: 1.05;
        letter-spacing: -0.02em; margin: 0.3rem 0 0.1rem 0;
    }}
    .st-key-hero .hero-small {{ color: #B9C3D6; font-size: 1.05rem; }}
    .st-key-hero .hero-question {{ color: #FFFFFF; font-size: 2.4rem; font-weight: 600; line-height: 1.15; }}

    /* Page section title with a short gold underline (quiet hero echo) */
    .section-title {{ font-size: 2.6rem; font-weight: 700; color: {NAVY};
        letter-spacing: -0.02em; line-height: 1.1; }}
    .section-rule {{ width: 64px; height: 5px; background: {GOLD}; border-radius: 3px;
        margin: 0.6rem 0 0.3rem 0; }}

    /* Numbered steps on page 1 */
    .step-num {{ font-size: 2.2rem; font-weight: 600; color: {GOLD}; line-height: 1; }}

    /* Verdict hero on page 6 (st.container with key="verdict") */
    .st-key-verdict {{
        background: {NAVY};
        border-radius: 6px;
        padding: 1.6rem 2rem;
        border-left: 8px solid {GOLD};
    }}
    .st-key-verdict p, .st-key-verdict h1, .st-key-verdict h2, .st-key-verdict h3 {{ color: #FFFFFF; }}
    .st-key-verdict .verdict-big {{
        color: #FFFFFF; font-size: 2.4rem; font-weight: 600; line-height: 1.12;
        letter-spacing: -0.02em;
    }}
    .st-key-verdict .verdict-sub {{ color: #B9C3D6; font-size: 1.05rem; margin-top: 0.5rem; }}
    .st-key-verdict .verdict-amount {{
        color: {GOLD_LIGHT}; font-size: 2.8rem; font-weight: 600; line-height: 1.05;
        letter-spacing: -0.02em;
    }}
    .st-key-verdict .verdict-amount-label {{ color: #B9C3D6; font-size: 1rem; }}

    /* Recommendation cards on page 6: no big number, a quiet left accent */
    .rec-card {{
        border-left: 3px solid {GOLD};
        padding: 0.1rem 0 0.1rem 0.9rem;
    }}
    .rec-card .rec-title {{ font-weight: 600; font-size: 1rem; color: {NAVY}; }}
    .rec-card .rec-text {{ color: {MUTED}; font-size: 0.9rem; line-height: 1.35; }}
    </style>
    """, unsafe_allow_html=True)


def tidy(chart):
    """Publication-quality chart defaults, shared by every page so all charts match.

    Thin axis lines, no gridlines, larger IBM Plex labels, muted colours.
    """
    return chart.configure_view(stroke=None).configure_axis(
        labelFontSize=13, titleFontSize=13, labelColor="#3A4459", titleColor=MUTED,
        grid=False, domainColor="#C7CDD9", domainWidth=1, tickColor="#C7CDD9", tickSize=4,
        labelFont="IBM Plex Sans", titleFont="IBM Plex Sans", labelPadding=4,
    ).configure_legend(labelFontSize=12, labelColor="#3A4459", titleColor=MUTED,
                       labelFont="IBM Plex Sans")


def section_title(text):
    """A page heading with a short gold underline: the hero's quiet little sibling."""
    import streamlit as st
    st.markdown(
        f"<div class='section-title'>{text}</div>"
        "<div class='section-rule'></div>", unsafe_allow_html=True)

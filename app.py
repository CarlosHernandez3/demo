import streamlit as st

# Add custom CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #16171b !important;

    }
    .element-container:has(.stMetric) {
        background-color: #1f2125; 
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    div[data-testid="stMetricValue"] {
        color: #f0f2f4 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #16171b !important; # fix this make it readable light grey 
    }
    div[data-testid="stSidebar"] {
        background-color: #16171b !important;
    }
    .block-container {
        background-color: #16171b !important;
        max-width: 75%;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    header[data-testid="stHeader"] {
        background-color: #16171b !important;
        color: #fff !important;
    }
    header[data-testid="stHeader"] * {
        color: #fff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


pages = [
    st.Page("chatbot.py"),
    st.Page("dashboard.py")
]
pg = st.navigation(pages, position="top")
pg.run()
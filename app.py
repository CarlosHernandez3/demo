import streamlit as st

# Add custom CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #16171b !important;
    }
    div[data-testid="stSidebar"] {
        background-color: #16171b !important;
    }
    .block-container {
        background-color: #16171b !important;
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
import streamlit as st

pages = [
    st.Page("chatbot.py"),
    st.Page("dashboard.py")
]
pg = st.navigation(pages, position="top")
pg.run()
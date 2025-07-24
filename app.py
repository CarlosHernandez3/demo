import streamlit as st

pg = st.navigation(st.Page("chatbot.py"), st.Page("dashboard.py"), position="top")
pg.run()
import streamlit as st

def add_member():
    st.session_state.members.append({
        "name": "",
        "availability": {date: "" for date in st.session_state.dates},
        "location": "",
        "hobbies": [],
        "favorite_foods": []
    })


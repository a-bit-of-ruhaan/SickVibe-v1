import json
import streamlit as st

try:
    with open("data/music.json", "r", encoding="utf-8") as file:
        SONGS_DATA = json.load(file)
except FileNotFoundError:
    st.error("Error: Could not find 'data/music.json'. Check your folder path!")
    SONGS_DATA = []

 
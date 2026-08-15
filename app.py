import streamlit as st
import json
import os

st.set_page_config(page_title="SickVibe", layout="wide")

# Inject Custom Orange/Black CSS
try:
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

@st.cache_data
def load_songs():
    try:
        with open("data/music.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

SONGS_DATA = load_songs()

# Brand Identity
st.markdown("<h1 style='color: #FFFFFF; font-weight: 800; margin-bottom: 0;'>Sick<span style='color: #FF6B00;'>Vibe</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 0.9rem; letter-spacing: 2px; margin-bottom: 25px;'>GET YOUR SICK VIBE HERE</p>", unsafe_allow_html=True)

# Search Input
search = st.text_input("", placeholder="What's your Vibe Today??").strip().lower()

# Handle data query matching logic
if search:
    results = [
        s for s in SONGS_DATA 
        if any(search in str(s.get(k, "")).lower() for k in ["title", "artist", "album"])
    ]
else:
    results = SONGS_DATA[:15]

DEFAULT_COVER = "images/default_cover.jpg"

def get_valid_cover(song_obj):
    img = song_obj.get("image", DEFAULT_COVER)
    return img if os.path.exists(img) else DEFAULT_COVER

# Track Index Splitting
featured_songs = results[:4]
remaining_songs = results[4:]

# --- FEATURED GRID TILES ---
if featured_songs:
    st.markdown("<h3 style='color: #FFFFFF; margin-bottom: 15px;'>Featured Vibes</h3>", unsafe_allow_html=True)
    tile_cols = st.columns(len(featured_songs))
    
    for idx, song in enumerate(featured_songs):
        with tile_cols[idx]:
            with st.container(border=True):
                st.image(get_valid_cover(song), width=500)
                st.markdown(f"<div class='song-title'>{song['title']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='song-artist'>{song['artist']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='song-album'>{song['album']} • {song['year']}</div>", unsafe_allow_html=True)
                st.audio(song["file"], format="audio/mp3")

# --- LIST TRACK VIEW ---
if remaining_songs:
    st.markdown("<br><h3 style='color: #FFFFFF; margin-bottom: 15px;'>More Tracks</h3>", unsafe_allow_html=True)
    
    for song in remaining_songs:
        # 1 part image space, 4 parts text descriptors, 5 parts media controller length
        cover_col, info_col, audio_col = st.columns([1, 4, 5])
        
        with cover_col:
            st.image(get_valid_cover(song), width=55)
            
        with info_col:
            st.markdown(f"<div class='list-title'>{song['title']}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='list-meta'><span class='list-meta-orange'>{song['artist']}</span> • {song['album']} ({song['year']})</div>", 
                unsafe_allow_html=True
            )
            
        with audio_col:
            st.audio(song["file"], format="audio/mp3")
        
        # Subtle horizontal orange gradient line break
        st.markdown("<div class='orange-divider'></div>", unsafe_allow_html=True)

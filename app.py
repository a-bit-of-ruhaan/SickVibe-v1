import streamlit as st
import json
import os
import base64
from pages.songpage import render_song_page

st.set_page_config(page_title="SickVibe", layout="wide")

CSS_CONTENT = ""
try:
    with open("styles/style.css", "r", encoding="utf-8") as f:
        CSS_CONTENT = f.read()
        st.markdown(f"<style>{CSS_CONTENT}</style>", unsafe_allow_html=True)
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

if "viewing_song" not in st.session_state:
    st.session_state.viewing_song = None
if "current_track_idx" not in st.session_state:
    st.session_state.current_track_idx = None
if "player_command" not in st.session_state:
    st.session_state.player_command = "STOP"

def get_audio_src(file_path):
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f"data:audio/mp3;base64,{b64}"

def render_global_audio():
    if st.session_state.current_track_idx is None:
        return
    
    current_song = SONGS_DATA[st.session_state.current_track_idx]
    audio_src = get_audio_src(current_song["file"])
    
    if not audio_src:
        st.warning(f"⚠️ Audio file not found: {current_song['file']}")
        return
    
    player_html = f"""
    <style>
        body {{ margin: 0; padding: 0; background: transparent; }}
        .sickvibe-player {{
            width: 100%;
            display: flex;
            flex-direction: column;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }}
        .player-controls {{
            display: flex;
            align-items: center;
            gap: 12px;
            width: 100%;
        }}
        .play-btn {{
            background: #FF5500;
            border: none;
            color: #FFFFFF;
            padding: 10px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }}
        .play-btn:hover {{
            background: rgba(255, 85, 0, 0.8);
            transform: scale(1.05);
        }}
        .seek-bar {{
            flex: 1;
            height: 6px;
            -webkit-appearance: none;
            appearance: none;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            outline: none;
            cursor: pointer;
        }}
        .seek-bar::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 14px;
            height: 14px;
            background: #FF5500;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(255, 85, 0, 0.25);
        }}
        .seek-bar::-moz-range-thumb {{
            width: 14px;
            height: 14px;
            background: #FF5500;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(255, 85, 0, 0.25);
        }}
        .time-display {{
            color: #8F8F94;
            font-size: 0.85rem;
            font-weight: 600;
            min-width: 45px;
            text-align: right;
        }}
    </style>
    <div class="sickvibe-player">
        <audio id="global-audio-element" src="{audio_src}"></audio>
        <div class="player-controls">
            <button class="play-btn" id="global-play-btn">▶</button>
            <input type="range" class="seek-bar" id="global-seek-bar" value="0" max="100">
            <span class="time-display" id="global-time-display">0:00</span>
        </div>
    </div>
    <script>
        try {{
            const audio = document.getElementById('global-audio-element');
            const btn = document.getElementById('global-play-btn');
            const seek = document.getElementById('global-seek-bar');
            const timeDisp = document.getElementById('global-time-display');
            
            btn.addEventListener('click', togglePlay);
            
            function togglePlay() {{
                if (audio.paused) {{
                    audio.play().catch(e => console.log("Playback error:", e));
                    btn.innerText = '⏸';
                }} else {{
                    audio.pause();
                    btn.innerText = '▶';
                }}
            }}

            audio.addEventListener('timeupdate', () => {{
                if (!isNaN(audio.duration)) {{
                    seek.value = (audio.currentTime / audio.duration) * 100;
                    let mins = Math.floor(audio.currentTime / 60);
                    let secs = Math.floor(audio.currentTime % 60);
                    if (secs < 10) secs = '0' + secs;
                    timeDisp.innerText = mins + ':' + secs;
                }}
            }});

            seek.addEventListener('change', () => {{
                if(audio.duration) {{
                    audio.currentTime = audio.duration * (seek.value / 100);
                }}
            }});

            audio.addEventListener('ended', () => {{
                const link = document.createElement('a');
                link.href = "?next_track=true&t=" + new Date().getTime();
                link.click();
            }});

            if ("{st.session_state.player_command}" === "PLAY") {{
                audio.play().catch(e => console.log("Autoplay waiting for click"));
                btn.innerText = '⏸';
            }}
        }} catch (e) {{
            console.error('Audio player error:', e);
        }}
    </script>
    """
    st.components.v1.html(player_html, height=85, scrolling=False)

query_params = st.query_params
if "next_track" in query_params:
    st.query_params.clear()
    if st.session_state.current_track_idx is not None:
        next_idx = st.session_state.current_track_idx + 1
        if next_idx < len(SONGS_DATA):
            st.session_state.current_track_idx = next_idx
            st.session_state.player_command = "PLAY"
            if st.session_state.viewing_song is not None:
                st.session_state.viewing_song = SONGS_DATA[next_idx]
        else:
            st.session_state.player_command = "STOP"
    st.rerun()

DEFAULT_COVER = "images/default_cover.jpg"

def get_valid_cover(song_obj):
    img = song_obj.get("image", DEFAULT_COVER)
    return img if os.path.exists(img) else DEFAULT_COVER

# --- SONG DETAIL SCREEN LOGIC MODIFICATION ---
if st.session_state.viewing_song is not None:
    # 1. Determine current playing position to populate subsequent rows
    current_idx = st.session_state.current_track_idx if st.session_state.current_track_idx is not None else 0
    
    # 2. Slice the next 3 tracks dynamically from the dataset 
    queue_tracks = SONGS_DATA[current_idx + 1 : current_idx + 4]
    
    # 3. Call the modified component layout function with 4 positional values
    render_song_page(st.session_state.viewing_song, queue_tracks, get_valid_cover, render_global_audio)
    
    # 4. Global Queue click detector state pipeline
    # Updates tracker values when interactive queue row buttons alter the view target
    if st.session_state.current_track_idx is not None:
        active_track = SONGS_DATA[st.session_state.current_track_idx]
        if st.session_state.viewing_song != active_track and "update_sync" in st.session_state:
            st.session_state.viewing_song = active_track
            st.rerun()

else:
    st.markdown("<h1 style='color: #FFFFFF; font-weight: 800; margin-bottom: 0;'>Sick<span style='color: #FF6B00;'>Vibe</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888888; font-size: 0.9rem; letter-spacing: 2px; margin-bottom: 25px;'>GET YOUR SICK VIBE HERE</p>", unsafe_allow_html=True)

    search = st.text_input("", placeholder="What's your Vibe Today??").strip().lower()

    if search:
        results = [
            s for s in SONGS_DATA 
            if any(search in str(s.get(k, "")).lower() for k in ["title", "artist", "album"])
        ]
    else:
        results = SONGS_DATA[:15]

    featured_songs = results[:4]
    remaining_songs = results[4:]

    if featured_songs:
        st.markdown("<h3 style='color: #FFFFFF; margin-bottom: 15px;'>Featured Vibes</h3>", unsafe_allow_html=True)
        tile_cols = st.columns(len(featured_songs))
        
        for idx, song in enumerate(featured_songs):
            global_idx = SONGS_DATA.index(song)
            with tile_cols[idx]:
                with st.container(border=True):
                    st.image(get_valid_cover(song), use_container_width=True)
                    st.markdown(f"<div class='song-title'>{song['title']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='song-artist'>{song['artist']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='song-album'>{song['album']} • {song['year']}</div>", unsafe_allow_html=True)
                    
                    if st.button("Play Vibe", key=f"btn_play_feat_{idx}", use_container_width=True):
                        st.session_state.current_track_idx = global_idx
                        st.session_state.player_command = "PLAY"
                        st.session_state.viewing_song = song  # Update detail visibility context
                        st.rerun()
                    
                    if st.button("View Info", key=f"btn_info_feat_{idx}", use_container_width=True):
                        st.session_state.viewing_song = song
                        st.rerun()

    if remaining_songs:
        st.markdown("<br><h3 style='color: #FFFFFF; margin-bottom: 15px;'>More Tracks</h3>", unsafe_allow_html=True)
        
        for idx, song in enumerate(remaining_songs):
            global_idx = SONGS_DATA.index(song)
            cover_col, info_col, action_col = st.columns([1, 6, 3])
            
            with cover_col:
                st.image(get_valid_cover(song), width=55)
                
            with info_col:
                st.markdown(f"<div class='list-title'>{song['title']}</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='list-meta'><span class='list-meta-orange'>{song['artist']}</span> • {song['album']} ({song['year']})</div>", 
                    unsafe_allow_html=True
                )
                
            with action_col:
                st.markdown("<div style='padding-top: 12px;'></div>", unsafe_allow_html=True)
                play_col, info_btn_col = st.columns(2)
                with play_col:
                    if st.button("Play", key=f"btn_play_list_{idx}", use_container_width=True):
                        st.session_state.current_track_idx = global_idx
                        st.session_state.player_command = "PLAY"
                        st.session_state.viewing_song = song
                        st.rerun()
                with info_btn_col:
                    if st.button("Details", key=f"btn_info_list_{idx}", use_container_width=True):
                        st.session_state.viewing_song = song
                        st.rerun()
            
            st.markdown("<div class='orange-divider'></div>", unsafe_allow_html=True)

    if st.session_state.current_track_idx is not None:
        st.markdown("<div style='position: fixed; bottom: 0; left: 0; width: 100%; z-index: 9999; padding: 10px 20px;'>", unsafe_allow_html=True)
        render_global_audio()

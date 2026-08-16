import streamlit as st
from functions.search import SONGS_DATA

def render_song_page(current_song, queue_tracks, get_valid_cover_func, render_audio_func):
    """
    Upgraded Song Page with fully functional queue tracking mechanics.
    
    Parameters:
        current_song (dict): The active song dictionary payload.
        queue_tracks (list): List of song dicts currently waiting in queue.
        get_valid_cover_func (func): Returns string URL/path for album arts.
        render_audio_func (func): Mounts native/custom playback runtime engines.
    """
    
    # ----------------------------------------------------
    # 1. TOP ACTIONS ROW
    # ----------------------------------------------------
    nav_col, _, fav_col = st.columns([1.5, 7.0, 1.5])
    
    with nav_col:
        if st.button("← Browse", type="secondary", key="back_to_browse", use_container_width=True):
            st.session_state.viewing_song = None
            st.rerun()
            
    with fav_col:
        track_id = current_song.get('id', current_song['title'])
        fav_key = f"fav_track_{track_id}"
        
        if fav_key not in st.session_state:
            st.session_state[fav_key] = False
            
        if st.session_state[fav_key]:
            if st.button("❤️ Liked", type="primary", key="fav_active", use_container_width=True):
                st.session_state[fav_key] = False
                st.rerun()
        else:
            if st.button("🖤 Like", type="secondary", key="fav_inactive", use_container_width=True):
                st.session_state[fav_key] = True
                st.rerun()

    # ----------------------------------------------------
    # 2. HERO DASHBOARD MATRIX (Optimized Layout Ratios)
    # ----------------------------------------------------
    img_col, center_profile_col, detail_col = st.columns([2.0, 3.5, 4.5], gap="medium")
    
    with img_col:
        st.markdown('<div class="song-cover-container">', unsafe_allow_html=True)
        st.image(get_valid_cover_func(current_song), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with center_profile_col:
        st.markdown(f"""
            <div class="profile-brand-card">
                <p class="deck-status-badge"> NOW PLAYING</p>
                <h1 class="track-main-title">{current_song["title"]}</h1>
                <p class="track-artist-sub">{current_song["artist"]}</p>
                <div class="sound-wave-icon"><span></span><span></span><span></span><span></span></div>
            </div>
        """, unsafe_allow_html=True)
        
    with detail_col:
        st.markdown('<div class="song-card-wrapper">', unsafe_allow_html=True)
        st.markdown('<p class="track-context-badge">TRACK DETAILS</p>', unsafe_allow_html=True)
        
        # Grid block structure to let existing CSS styles distribute evenly
        st.markdown('<div class="meta-pill-vertical-stack">', unsafe_allow_html=True)
        
        col_meta_1, col_meta_2 = st.columns(2)
        with col_meta_1:
            st.markdown(f'<div class="meta-pill"><span class="meta-lbl">Album  </span><span class="meta-val">{current_song["album"]}</span></div>', unsafe_allow_html=True)
            if "genre" in current_song:
                st.markdown(f'<div class="meta-pill"><span class="meta-lbl">Genre  </span><span class="meta-val">{current_song["genre"]}</span></div>', unsafe_allow_html=True)
        with col_meta_2:
            st.markdown(f'<div class="meta-pill"><span class="meta-lbl">Released  </span><span class="meta-val">{current_song["year"]}</span></div>', unsafe_allow_html=True)
            if "duration" in current_song:
                st.markdown(f'<div class="meta-pill"><span class="meta-lbl">Length  </span><span class="meta-val">{current_song["duration"]}</span></div>', unsafe_allow_html=True)
                
        st.markdown('</div></div>', unsafe_allow_html=True)

    # ----------------------------------------------------
    # 3. CONSOLE & INTERACTIVE QUEUE DECK
    # ----------------------------------------------------
    player_deck_col, layout_sidebar_col = st.columns([5.5, 4.5], gap="medium")

    with player_deck_col:
        st.markdown('<div class="master-playback-console-full">', unsafe_allow_html=True)
        st.markdown('<p class="console-label">MUSIC PLAYBACK</p>', unsafe_allow_html=True)
        
        # Audio elements mount safely here
        render_audio_func()
        
        st.markdown('</div>', unsafe_allow_html=True)

    with layout_sidebar_col:
        st.markdown('<div class="queue-panel-container">', unsafe_allow_html=True)
        st.markdown('<p class="queue-header-label">NEXT IN PLAYER QUEUE</p>', unsafe_allow_html=True)
        
        # Loop through queue items dynamically to replace static HTML lines
        for idx, next_song in enumerate(queue_tracks, start=2):
            q_row_id = next_song.get('id', next_song['title'])
            
            # Interactive container row using clean Streamlit layout splits
            st.markdown(f'<div class="queue-row" id="queue-item-{q_row_id}">', unsafe_allow_html=True)
            idx_col, track_info_col, action_col = st.columns([1, 6, 3])
            
            with idx_col:
                st.markdown(f'<div class="q-index">{idx:02d}</div>', unsafe_allow_html=True)
                
            with track_info_col:
                st.markdown(f"""
                    <div class="q-details">
                        <p class="q-title" style="margin:0; font-weight:600;">{next_song["title"]}</p>
                        <p class="q-artist" style="margin:0; opacity:0.7; font-size:0.85rem;">{next_song["artist"]}</p>
                    </div>
                """, unsafe_allow_html=True)
                
            with action_col:
                if st.button("Play Next ➔", key=f"skip_to_{q_row_id}_{idx}", type="secondary", use_container_width=True):
        # We find the matching track position out of the full catalog dataset array
        # This triggers a clean index pointer swap in the main execution pipeline
                   st.session_state.current_track_idx = SONGS_DATA.index(next_song)
                   st.session_state.player_command = "PLAY"
                   st.session_state.viewing_song = next_song
                   st.session_state.update_sync = True
                   st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

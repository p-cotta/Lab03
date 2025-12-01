import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Music Explorer")

BASE_URL = "https://www.theaudiodb.com/api/v1/json/2/"

@st.cache_data(ttl=3600)
def search_artist(artist_name):
    """Search for artist by name"""
    endpoint = f"{BASE_URL}search.php"
    params = {'s': artist_name}
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        
        # Check if response is valid JSON
        content = response.text.strip()
        if not content:
            return None
            
        return response.json()
    except Exception as e:
        return None

@st.cache_data(ttl=3600)
def get_artist_discography(artist_id):
    """Get artist's full discography"""
    if not artist_id:
        return None
        
    endpoint = f"{BASE_URL}album.php"
    params = {'i': artist_id}
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        
        content = response.text.strip()
        if not content:
            return {"album": []}
            
        data = response.json()
        return data
    except Exception as e:
        return {"album": []}

@st.cache_data(ttl=3600)
def get_artist_top_tracks(artist_name):
    """Get artist's top tracks - uses artist name instead of ID"""
    if not artist_name:
        return {"track": []}
        
    endpoint = f"{BASE_URL}track-top10.php"
    params = {'s': artist_name}
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        
        content = response.text.strip()
        if not content or content == "null":
            return {"track": []}
            
        data = response.json()
        
        # If API returns null instead of proper JSON structure
        if data is None:
            return {"track": []}
            
        return data
    except Exception as e:
        return {"track": []}

def safe_int(value):
    """Safely convert to integer"""
    try:
        if value in [None, "", "0", 0, "null"]:
            return 0
        return int(float(value))
    except:
        return 0

def main():
    st.title("🎵 Music Explorer Pro")
    st.markdown("Explore artist discographies and track popularity with interactive visualizations")
    
    # Sidebar for user inputs
    with st.sidebar:
        st.header("🔍 Search Settings")
        
        # First user input: Artist search
        artist_name = st.text_input(
            "Enter Artist Name:",
            placeholder="e.g., Coldplay, Taylor Swift...",
            help="Search for any musical artist"
        )
        
        # Second user input: Visualization type
        viz_type = st.selectbox(
            "Chart Type:",
            ["Artist Overview", "Discography Analysis", "Popular Tracks"],
            help="Choose how to visualize the artist data"
        )
        
        # Third user input: Additional options based on viz type
        if viz_type == "Popular Tracks":
            min_popularity = st.slider(
                "Minimum popularity:",
                min_value=0,
                max_value=100,
                value=0,
                help="Filter tracks by minimum popularity score"
            )
        elif viz_type == "Discography Analysis":
            sort_by = st.selectbox(
                "Sort albums by:",
                ["Year (Newest First)", "Year (Oldest First)", "Sales", "Track Count"]
            )

    # Main content area
    if artist_name:
        with st.spinner(f"Searching for {artist_name}..."):
            search_data = search_artist(artist_name)
            
            if not search_data or not search_data.get("artists"):
                st.error("No artist found. Please check the spelling or try another artist.")
                st.info("💡 Try: Coldplay, Taylor Swift, Ed Sheeran, Beyonce, Daft Punk, The Beatles")
                return
            
            artist = search_data["artists"][0]
            artist_id = artist.get("idArtist")
            
            if not artist_id:
                st.error("No artist ID found.")
                return
            
            # Display artist header - FIXED LAYOUT
            st.subheader(f"🎤 {artist.get('strArtist', 'Unknown Artist')}")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Dynamic image display - FIXED deprecated parameter
                fanart = artist.get("strArtistFanart")
                if fanart:
                    st.image(fanart, use_container_width=True, caption=f"{artist.get('strArtist', 'Artist')}")
                else:
                    st.info("🎨 No artist image available")
            
            with col2:
                # Artist metrics in a better layout
                st.markdown("### Artist Information")
                
                info_col1, info_col2, info_col3 = st.columns(3)
                with info_col1:
                    st.metric("Genre", artist.get('strGenre', 'N/A'))
                with info_col2:
                    st.metric("Formed", artist.get('intFormedYear', 'N/A'))
                with info_col3:
                    st.metric("Country", artist.get('strCountry', 'N/A'))
                
                # Dynamic biography display
                bio = artist.get("strBiographyEN", "")
                if bio and bio != "No biography available." and len(bio) > 10:
                    with st.expander("📖 Read Biography"):
                        # Clean up biography text
                        clean_bio = ' '.join(bio.split())
                        st.write(clean_bio[:800] + "..." if len(clean_bio) > 800 else clean_bio)
                else:
                    st.write("_No biography available_")
            
            st.divider()
            
            # Fetch and process data based on visualization type
            if viz_type == "Artist Overview":
                display_artist_overview(artist, artist_id)
            elif viz_type == "Discography Analysis":
                display_discography_analysis(artist_id, artist.get("strArtist"), sort_by)
            else:
                display_popular_tracks(artist.get("strArtist"), min_popularity)

def display_artist_overview(artist, artist_id):
    """Display comprehensive artist overview"""
    st.subheader("📊 Artist Overview")
    
    # Key metrics grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Music Genre", artist.get('strGenre', 'N/A'))
    with col2:
        formed_year = artist.get('intFormedYear', 'N/A')
        if formed_year != 'N/A':
            years_active = datetime.now().year - int(formed_year)
            st.metric("Years Active", f"{years_active} years")
        else:
            st.metric("Years Active", "N/A")
    with col3:
        st.metric("Country", artist.get('strCountry', 'N/A'))
    with col4:
        st.metric("Artist ID", artist_id)
    
    # Style badges
    st.subheader("🎵 Musical Style")
    style = artist.get('strStyle', '')
    if style:
        styles = [s.strip() for s in style.split(',')]
        style_text = " • ".join(styles[:6])  # Show first 6
        st.write(style_text)
    else:
        st.write("_No style information available_")
    
    # Social links w emojis
    st.subheader("🌐 Online Presence")
    social_data = [
        ("🌐 Website", artist.get('strWebsite')),
        ("📘 Facebook", artist.get('strFacebook')),
        ("🐦 Twitter", artist.get('strTwitter')),
        ("📷 Instagram", artist.get('strInstagram'))
    ]
    
    # Only show available social links
    available_links = [(platform, url) for platform, url in social_data if url]
    
    if available_links:
        cols = st.columns(len(available_links))
        for idx, (platform, url) in enumerate(available_links):
            with cols[idx]:
                st.markdown(f"[{platform}]({url})")
    else:
        st.write("_No social links available_")

def display_discography_analysis(artist_id, artist_name, sort_by):
    """Display discography analysis"""
    st.subheader("💿 Discography Analysis")
    
    discography = get_artist_discography(artist_id)
    
    if not discography or not discography.get("album"):
        st.warning("No discography data available from the API.")
        st.info("This artist's album data is currently unavailable.")
        return
    
    album_data = discography["album"]
    
    # Process album data
    processed_albums = []
    for album in album_data:
        year = safe_int(album.get("intYearReleased"))
        if year > 1900:  # Filter out too old years
            processed_albums.append({
                "Album": album.get("strAlbum", "Unknown Album"),
                "Year": year,
                "Genre": album.get("strGenre", "Unknown"),
                "Sales": safe_int(album.get("intSales")),
                "Tracks": safe_int(album.get("intTotalTracks"))
            })
    
    if not processed_albums:
        st.warning("No valid album data to display.")
        return
    
    df = pd.DataFrame(processed_albums)
    
    # Sort based on user select
    if sort_by == "Year (Newest First)":
        df = df.sort_values("Year", ascending=False)
    elif sort_by == "Year (Oldest First)":
        df = df.sort_values("Year", ascending=True)
    elif sort_by == "Sales":
        df = df.sort_values("Sales", ascending=False)
    elif sort_by == "Track Count":
        df = df.sort_values("Tracks", ascending=False)
    
    # Display album count w stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Albums", len(df))
    with col2:
        st.metric("Years Span", f"{df['Year'].min()} - {df['Year'].max()}")
    with col3:
        st.metric("Most Tracks", df['Tracks'].max())
    
    # Album timeline chart
    if len(df) > 1:
        st.write("### 📅 Albums by Release Year")
        year_counts = df['Year'].value_counts().sort_index()
        st.bar_chart(year_counts)
    
    # Album details table
    st.write("### 💽 Album Catalog")
    st.dataframe(
        df[['Album', 'Year', 'Tracks', 'Sales']], 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Album": "Album Name",
            "Year": "Release Year", 
            "Tracks": "Track Count",
            "Sales": "Sales (Est.)"
        }
    )

def display_popular_tracks(artist_name, min_popularity):
    """Display popular tracks analysis - shows only actual data from database"""
    st.subheader("🔥 Popular Tracks Analysis")
    
    # Get top tracks
    top_tracks_data = get_artist_top_tracks(artist_name)
    
    if not top_tracks_data or not top_tracks_data.get("track"):
        st.error("❌ No track data available from the database for this artist.")
        st.info("The AudioDB API does not have top tracks data for this artist in their database.")
        return
    
    tracks = top_tracks_data["track"]
    
    # Show how many tracks we found
    st.success(f"📊 Found {len(tracks)} tracks in the database!")
    
    # Process track data
    track_data = []
    for track in tracks:
        popularity = safe_int(track.get("intLoved"))
        track_data.append({
            "Track": track.get("strTrack", "Unknown Track"),
            "Popularity": popularity,
            "Album": track.get("strAlbum", "Unknown Album"),
            "Year": safe_int(track.get("intYearReleased")),
            "Duration": safe_int(track.get("intDuration")),
            "Video": track.get("strMusicVid")
        })
    
    if not track_data:
        st.error("❌ No track data to display.")
        return
    
    df = pd.DataFrame(track_data)
    
    # Filter by popularity
    filtered_df = df[df['Popularity'] >= min_popularity]
    
    if filtered_df.empty:
        st.warning(f"❌ No tracks meet the minimum popularity score of {min_popularity}.")
        st.info(f"Try lowering the minimum popularity filter to see more tracks.")
        return
    
    # Display track count
    st.metric("Tracks Showing", len(filtered_df))
    
    # Popularity chart
    st.write("### 📊 Track Popularity Chart")
    chart_data = filtered_df.set_index('Track')['Popularity'].sort_values(ascending=True)
    st.bar_chart(chart_data)
    
    # Track details
    st.write("### 🎵 Track Details")
    
    for _, track in filtered_df.sort_values('Popularity', ascending=False).iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{track['Track']}**")
                st.write(f"*{track['Album']} ({track['Year']})*")
            
            with col2:
                # Color code popularity
                popularity = track['Popularity']
                if popularity >= 80:
                    color = "🟢"
                elif popularity >= 60:
                    color = "🟡" 
                else:
                    color = "🔴"
                st.write(f"{color} **{popularity}**")
            
            with col3:
                if track['Video']:
                    st.markdown(f"[🎬 Watch]({track['Video']})", unsafe_allow_html=True)
                else:
                    st.write("_No video_")
            
            st.divider()

if __name__ == "__main__":
    main()

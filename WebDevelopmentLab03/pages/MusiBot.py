import streamlit as st
import requests
import google.generativeai as genai

st.title("MUSIBOT 🎵🤖")

key = "AIzaSyC_Q4tP2_-QzJaRa2GVu95gVLB4O9amh44"  
genai.configure(api_key=key)
model = genai.GenerativeModel("gemini-2.5-flash")

def get_artist_info(artist_name):
    """Fetch artist data from AudioDB API"""
    url = f"https://theaudiodb.com/api/v1/json/2/search.php?s={artist_name}"
    response = requests.get(url)
    data = response.json()
    
    if data.get("artists"):
        artist = data["artists"][0]
        return {
            "name": artist.get("strArtist"),
            "genre": artist.get("strGenre"),
            "style": artist.get("strStyle")
        }
    return None

artist_name = st.text_input("Enter artist name for context:")
artist_info = None

if artist_name:
    artist_info = get_artist_info(artist_name)
    if artist_info:
        st.success(f"Artist context loaded: {artist_info['name']}")
    else:
        st.error("Artist not found!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

chatPrompt = st.chat_input("Type prompt here")

if chatPrompt:
    with st.chat_message("user"):
        st.write(chatPrompt)
    
    st.session_state.messages.append({"role": "user", "content": chatPrompt})
    
    if artist_info:
        context = f"You are a music expert. The user likes {artist_info['name']} ({artist_info['genre']} genre, {artist_info['style']} style). "
    else:
        context = "You are a music expert. "
    
    full_prompt = context + f"Respond to this: {chatPrompt}"
    
    try:
        response = model.generate_content(full_prompt)
        ai_response = response.text
    except Exception as e:
        ai_response = f"Error: {str(e)}"
    
    with st.chat_message("assistant"):
        st.write(ai_response)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

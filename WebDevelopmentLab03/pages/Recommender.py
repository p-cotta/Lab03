import streamlit as st
import requests
import google.generativeai as genai

st.title("RECOMMENDER")

key="AIzaSyC_Q4tP2_-QzJaRa2GVu95gVLB4O9amh44"
genai.configure(api_key=key)   
model = genai.GenerativeModel("gemini-2.5-flash") 
def get_artist_info(artist_name):
    url = f"https://theaudiodb.com/api/v1/json/2/search.php?s={artist_name}"
    r = requests.get(url)
    data = r.json()

    if data["artists"] is None:
        return None
    
    artist = data["artists"][0]
    return {
        "name": artist.get("strArtist"),
        "genre": artist.get("strGenre"),
        "style": artist.get("strStyle"),
        "mood": artist.get("strMood")
    }



artist1 = st.text_input("Enter Fav Artist 1!")
artist2 = st.text_input("Enter Fav Artist 2")

if st.button("Get recommendation!"):
    if not artist1 or not artist2:
        st.error("Please enter two artists!")
        st.stop()

    a1 = get_artist_info(artist1)
    a2 = get_artist_info(artist2)

    if a1 is None:
        st.error(f"Artist '{artist1}' not found.")
        st.stop()
    if a2 is None:
        st.error(f"Artist '{artist2}' not found.")
        st.stop()

    st.write("### Artist Data Fetched:")
    st.json({"Artist 1": a1, "Artist 2": a2})

    prompt = f"""
    The user likes these two artists:

    Artist 1:
    Name: {a1['name']}
    Genre: {a1['genre']}
    Style: {a1['style']}
    Mood: {a1['mood']}

    Artist 2:
    Name: {a2['name']}
    Genre: {a2['genre']}
    Style: {a2['style']}
    Mood: {a2['mood']}

    Based on both artists, recommend ONE music artist they would probably enjoy.
    Also list 3–5 top songs by your recommended artist.
    Make the explanation clear and friendly.
    """

    response = model.generate_content(prompt)

    st.subheader("Recommendation!")
    st.write(response.text)


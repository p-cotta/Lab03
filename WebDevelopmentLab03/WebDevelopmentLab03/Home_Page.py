import streamlit as st

# Title of App
st.title("Web Development Lab03")

# Assignment Data 
# TODO: Fill out your team number, section, and team members

st.header("CS 1301")
st.subheader("Team 10, Web Development - Section C")
st.subheader("Paul Cotter, Gavin Huey, Aayush Mohapatra")


# Introduction
# TODO: Write a quick description for all of your pages in this lab below, in the form:
#       1. **Page Name**: Description
#       2. **Page Name**: Description
#       3. **Page Name**: Description
#       4. **Page Name**: Description

st.write("""
Welcome to our Streamlit Web Development Lab03 app! You can navigate between the pages using the sidebar to the left. The following pages are:

1.SongInfo: A song searching tool that provides information for tracks based off what artist you input. \n
2.Recommender: A tool to recommend artists based off of artists you have already listened to. A list of potential artists is generated using Google Gemini API. \n
3.MusiBot: A music chatbot that you can ask any song, artist, or genre related question.

""")


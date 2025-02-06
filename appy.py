import streamlit as st
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
import os
from io import BytesIO
from analysis import clean_text, tokenize_and_filter, analyze_emotions, sentiment_analysis, plot_emotions
from database import (
    create_users_table,
    insert_user,
    authenticate_user,
    reset_password,
    check_user_exists,
    create_comments_table,
    insert_comment,
)

# Create database tables
create_users_table()
create_comments_table()

# Initialize session state variables
if 'page' not in st.session_state:
    st.session_state.page = "Login"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stButton button { 
        background-color: #4CAF50; 
        color: white; 
        border-radius: 5px; 
        padding: 10px 20px; 
        font-size: 16px; 
    }
    .stButton button:hover { background-color: #45a049; }
    .stTextInput input { 
        border-radius: 5px; 
        padding: 10px; 
        font-size: 16px; 
    }
    .stTitle { 
        font-size: 36px; 
        font-weight: bold; 
        color: #2E86C1; 
    }
    .stSubheader { 
        font-size: 24px; 
        color: #2E86C1; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Authentication Pages
# ----------------------------
if st.session_state.page == "Login":
    st.markdown("<div class='stTitle'>Login</div>", unsafe_allow_html=True)
    username = st.text_input('Username', placeholder="Enter your username")
    password = st.text_input('Password', type='password', placeholder="Enter your password")

    if st.button("Login"):
        if not username or not password:
            st.error("Please provide both username and password.")
        else:
            user = authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "Home"
            else:
                st.error("Invalid username or password")

    if st.button("Forgot Password?"):
        st.session_state.page = "Reset Password"

    if st.button("Register"):
        st.session_state.page = "Register"

elif st.session_state.page == "Register":
    st.markdown("<div class='stTitle'>Register</div>", unsafe_allow_html=True)
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    email = st.text_input('Email')

    if st.button("Register"):
        if not username or not password or not email:
            st.error("Please fill out all fields.")
        elif check_user_exists(username):
            st.error("Username already exists. Choose a different one.")
        else:
            insert_user(username, password, email)
            st.success("User registered successfully! Please login.")
            st.session_state.page = "Login"

elif st.session_state.page == "Reset Password":
    st.markdown("<div class='stTitle'>Reset Password</div>", unsafe_allow_html=True)
    username = st.text_input('Username')
    new_password = st.text_input('New Password', type='password')

    if st.button("Reset Password"):
        if not username or not new_password:
            st.error("Please provide username and new password.")
        else:
            reset_password(username, new_password)
            st.success("Password reset successfully! Please login.")
            st.session_state.page = "Login"

# ----------------------------
# Home Page – Voice Analysis
# ----------------------------
elif st.session_state.page == "Home":
    st.markdown(f"<div class='stTitle'>Welcome, {st.session_state.username}!</div>", unsafe_allow_html=True)
    st.markdown("<div class='stSubheader'>Record your voice note for sentiment analysis</div>", unsafe_allow_html=True)

    # Instead of sounddevice (which causes PortAudio errors on Streamlit Cloud),
    # we use the browser-based st_audiorecorder.
    from streamlit_audiorecorder import st_audiorecorder

    audio_bytes = st_audiorecorder("Press to record your voice note")
    
    # Display the audio player if recording is available
    if audio_bytes is not None:
        st.audio(audio_bytes, format="audio/wav")
    
        if st.button("📤 Analyze Audio"):
            filename = "recorded_audio.wav"
            with open(filename, "wb") as f:
                f.write(audio_bytes)
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(filename) as source:
                audio_data = recognizer.record(source)
            try:
                comment = recognizer.recognize_google(audio_data)
                st.write("🗣️ You said:", comment)

                # Analyze the recognized text
                cleansed_text = clean_text(comment)
                final_words = tokenize_and_filter(cleansed_text)
                emotions = analyze_emotions(final_words)
                sentiment = sentiment_analysis(cleansed_text)

                st.write(f"📊 Sentiment: {sentiment.capitalize()}")
                st.pyplot(plot_emotions(emotions))

                # Save the comment and analysis to the database
                insert_comment(
                    st.session_state.username,
                    comment,
                    sentiment,
                    "Unknown",
                    "Unknown",
                    "Unknown",
                    "Unknown"
                )
                st.success("✅ Voice note submitted successfully!")
            except sr.UnknownValueError:
                st.error("❌ Speech Recognition could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"❌ Could not request results from Speech Recognition service: {e}")
            os.remove(filename)

elif st.session_state.page == "About Us":
    st.markdown("<div class='stTitle'>About Us</div>", unsafe_allow_html=True)
    st.write(
        """### 🎤 Voice Sentiment Analysis
This tool helps users assess their stress levels by analyzing voice input.
Record a short message, and our AI will analyze the emotional content."""
    )

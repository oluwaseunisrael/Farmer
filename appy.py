import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
import os
from analysis import clean_text, tokenize_and_filter, analyze_emotions, sentiment_analysis, plot_emotions
from database import create_users_table, insert_user, authenticate_user, reset_password, check_user_exists, \
    create_comments_table, insert_comment

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
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'recording_start_time' not in st.session_state:
    st.session_state.recording_start_time = None

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stButton button { background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px 20px; font-size: 16px; }
    .stButton button:hover { background-color: #45a049; }
    .stTextInput input { border-radius: 5px; padding: 10px; font-size: 16px; }
    .stTitle { font-size: 36px; font-weight: bold; color: #2E86C1; }
    .stSubheader { font-size: 24px; color: #2E86C1; }
    .wave { width: 100%; height: 50px; background-image: url('https://upload.wikimedia.org/wikipedia/commons/a/a9/Wave_animated.gif'); background-repeat: no-repeat; background-size: cover; }
    </style>
    """,
    unsafe_allow_html=True
)

# Navigation Bar
if st.session_state.logged_in:
    st.markdown("---")
    nav_options = st.columns([1, 1, 1])
    with nav_options[0]:
        if st.button("🏠 Home"):
            st.session_state.page = "Home"
    with nav_options[1]:
        if st.button("ℹ️ About Us"):
            st.session_state.page = "About Us"
    with nav_options[2]:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.page = "Login"

# Authentication Pages
if st.session_state.page == "Login":
    st.markdown("<div class='stTitle'>Login</div>", unsafe_allow_html=True)
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    if st.button("Login"):
        user = authenticate_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "Home"
        else:
            st.error("Invalid username or password")
    if st.button("Register"):
        st.session_state.page = "Register"

elif st.session_state.page == "Register":
    st.markdown("<div class='stTitle'>Register</div>", unsafe_allow_html=True)
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    if st.button("Register"):
        if check_user_exists(username):
            st.error("Username already exists.")
        else:
            insert_user(username, password, "")
            st.success("Registration successful! Please login.")
            st.session_state.page = "Login"

# Home Page - Voice Analysis
elif st.session_state.page == "Home":
    st.markdown(f"<div class='stTitle'>Welcome, {st.session_state.username}!</div>", unsafe_allow_html=True)
    fs = 44100
    duration = 300
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎤 Start Recording") and not st.session_state.recording:
            st.session_state.recording = True
            st.session_state.audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            st.markdown('<div class="wave"></div>', unsafe_allow_html=True)
    with col2:
        if st.session_state.recording:
            if st.button("⏹ Stop Recording"):
                sd.stop()
                st.session_state.recording = False
                st.success("✅ Recording stopped!")
    with col3:
        if st.session_state.audio_data is not None:
            if st.button("📤 Submit for Analysis"):
                filename = "recorded_audio.wav"
                wav.write(filename, fs, st.session_state.audio_data)
                recognizer = sr.Recognizer()
                with sr.AudioFile(filename) as source:
                    audio_data = recognizer.record(source)
                try:
                    comment = recognizer.recognize_google(audio_data)
                    st.write("🗣️ You said:", comment)
                    cleansed_text = clean_text(comment)
                    final_words = tokenize_and_filter(cleansed_text)
                    emotions = analyze_emotions(final_words)
                    sentiment = sentiment_analysis(cleansed_text)
                    st.write(f"📊 Sentiment: {sentiment.capitalize()}")
                    st.pyplot(plot_emotions(emotions))
                    insert_comment(st.session_state.username, comment, sentiment, "Unknown", "Unknown", "Unknown", "Unknown")
                    st.success("✅ Voice note submitted successfully!")
                except sr.UnknownValueError:
                    st.error("❌ Could not understand the audio.")
                except sr.RequestError as e:
                    st.error(f"❌ Request error: {e}")
                os.remove(filename)

elif st.session_state.page == "About Us":
    st.markdown("<div class='stTitle'>About Us</div>", unsafe_allow_html=True)
    st.write("### 🎤 Voice Sentiment Analysis\nThis tool helps users assess their stress levels by analyzing voice input.")

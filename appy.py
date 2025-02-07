import streamlit as st
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
import os

def authenticate_user(username, password):
    return username == "admin" and password == "password"

def check_user_exists(username):
    return False

def insert_user(username, password, email):
    pass

def reset_password(username, new_password):
    pass

def clean_text(text):
    return text.lower()

def tokenize_and_filter(text):
    return text.split()

def analyze_emotions(words):
    return {"happy": 0.5, "sad": 0.3, "neutral": 0.2}

def sentiment_analysis(text):
    return "positive"

def insert_comment(username, comment, sentiment, param1, param2, param3, param4):
    pass

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

st.sidebar.title("Navigation")
if st.session_state.logged_in:
    if st.sidebar.button("🏠 Home"):
        st.session_state.page = "Home"
    if st.sidebar.button("ℹ️ About Us"):
        st.session_state.page = "About Us"
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = "Login"
        st.experimental_rerun()

if st.session_state.page == "Login":
    st.title("Login")
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "Home"
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
    
    if st.button("Register"):
        st.session_state.page = "Register"
        st.experimental_rerun()
    
    if st.button("Forgot Password"):
        st.session_state.page = "Reset Password"
        st.experimental_rerun()

elif st.session_state.page == "Register":
    st.title("Register")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    email = st.text_input("Email")
    
    if st.button("Submit"):
        if check_user_exists(new_username):
            st.error("Username already exists!")
        else:
            insert_user(new_username, new_password, email)
            st.success("Registration successful!")
            st.session_state.page = "Login"
            st.experimental_rerun()
    
    if st.button("Back to Login"):
        st.session_state.page = "Login"
        st.experimental_rerun()

elif st.session_state.page == "Reset Password":
    st.title("Reset Password")
    reset_username = st.text_input("Username")
    new_password = st.text_input("New Password", type="password")
    
    if st.button("Reset"):
        reset_password(reset_username, new_password)
        st.success("Password reset successful!")
        st.session_state.page = "Login"
        st.experimental_rerun()
    
    if st.button("Back to Login"):
        st.session_state.page = "Login"
        st.experimental_rerun()

elif st.session_state.page == "Home":
    st.title(f"Welcome, {st.session_state.username}!")
    st.subheader("Record your voice note for sentiment analysis")

    fs = 44100
    duration = 5
    
    if st.button("🎤 Start Recording"):
        st.session_state.recording = True
        st.session_state.audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        st.success("✅ Recording finished!")
        st.session_state.recording = False
    
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
                insert_comment(st.session_state.username, comment, sentiment, "Unknown", "Unknown", "Unknown", "Unknown")
                st.success("✅ Voice note submitted successfully!")
            except sr.UnknownValueError:
                st.error("❌ Speech Recognition could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"❌ Could not request results from Speech Recognition service: {e}")
            os.remove(filename)

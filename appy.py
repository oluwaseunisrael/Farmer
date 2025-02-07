import streamlit as st
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
import os

def authenticate_user(username, password):
    return username in users and users[username]['password'] == password

def check_user_exists(username):
    return username in users

def insert_user(username, password, email):
    users[username] = {'password': password, 'email': email}

def reset_password(username, new_password):
    if username in users:
        users[username]['password'] = new_password
        return True
    return False

def clean_text(text):
    return text.lower()

def tokenize_and_filter(text):
    return text.split()

def analyze_emotions(words):
    return {"happy": 0.5, "sad": 0.3, "neutral": 0.2}

def sentiment_analysis(text):
    return "positive"

def insert_comment(username, comment, sentiment):
    comments.append({"username": username, "comment": comment, "sentiment": sentiment})

users = {}
comments = []

if 'page' not in st.session_state:
    st.session_state.page = "Login"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None

st.title("🎙️ Voice Sentiment Analysis App")

if st.session_state.logged_in:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = "Login"
        st.rerun()

if st.session_state.page == "Login":
    st.header("Login")
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "Home"
            st.rerun()
        else:
            st.error("Invalid username or password")
    
    if st.button("Register"):
        st.session_state.page = "Register"
        st.rerun()
    
    if st.button("Forgot Password"):
        st.session_state.page = "Forgot Password"
        st.rerun()

elif st.session_state.page == "Register":
    st.header("Register")
    new_username = st.text_input("Username")
    new_email = st.text_input("Email")
    new_password = st.text_input("Password", type='password')
    
    if st.button("Sign Up"):
        if check_user_exists(new_username):
            st.error("Username already exists!")
        else:
            insert_user(new_username, new_password, new_email)
            st.success("Registration successful! You can now log in.")
            st.session_state.page = "Login"
            st.rerun()
    
    if st.button("Back to Login"):
        st.session_state.page = "Login"
        st.rerun()

elif st.session_state.page == "Forgot Password":
    st.header("Reset Password")
    username = st.text_input("Enter your username")
    new_password = st.text_input("Enter new password", type='password')
    
    if st.button("Reset Password"):
        if reset_password(username, new_password):
            st.success("Password reset successful! You can now log in.")
            st.session_state.page = "Login"
            st.rerun()
        else:
            st.error("Username not found!")
    
    if st.button("Back to Login"):
        st.session_state.page = "Login"
        st.rerun()

elif st.session_state.page == "Home":
    st.header(f"Welcome, {st.session_state.username}!")
    st.subheader("Record your voice note for sentiment analysis")
    fs = 44100
    duration = 5
    
    if st.button("🎤 Start Recording"):
        st.session_state.audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        st.success("✅ Recording finished!")
    
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
                insert_comment(st.session_state.username, comment, sentiment)
                st.success("✅ Voice note submitted successfully!")
            except sr.UnknownValueError:
                st.error("❌ Speech Recognition could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"❌ Could not request results: {e}")
            os.remove(filename)

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
            st.rerun()

# Authentication Pages
if st.session_state.page == "Login":
    st.markdown("<div class='stTitle'>Login</div>", unsafe_allow_html=True)
    username = st.text_input('Username', placeholder="Enter your username")
    password = st.text_input('Password', type='password', placeholder="Enter your password")
    
    if st.button("Login"):
        if not username or not password:
            st.error("Please provide both username and password.")
        else:
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
    st.markdown("<div class='stTitle'>Register</div>", unsafe_allow_html=True)
    new_username = st.text_input("New Username")
    new_email = st.text_input("Email")
    new_password = st.text_input("New Password", type='password')
    
    if st.button("Sign Up"):
        if check_user_exists(new_username):
            st.error("Username already exists!")
        else:
            insert_user(new_username, new_password, new_email)
            st.success("Registration successful! Please login.")
            st.session_state.page = "Login"
            st.rerun()

elif st.session_state.page == "Forgot Password":
    st.markdown("<div class='stTitle'>Reset Password</div>", unsafe_allow_html=True)
    reset_username = st.text_input("Username")
    new_password = st.text_input("New Password", type='password')
    
    if st.button("Reset"):
        reset_password(reset_username, new_password)
        st.success("Password reset successful! Please login.")
        st.session_state.page = "Login"
        st.rerun()

elif st.session_state.page == "Home":
    st.markdown(f"<div class='stTitle'>Welcome, {st.session_state.username}!</div>", unsafe_allow_html=True)
    st.markdown("<div class='stSubheader'>Record your voice note for sentiment analysis</div>", unsafe_allow_html=True)

    fs = 44100  # Sample rate
    duration = 5  # Seconds

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎤 Start Recording"):
            st.session_state.audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            st.markdown('<div class="wave"></div>', unsafe_allow_html=True)
            sd.wait()
            st.success("✅ Recording finished!")
    
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
                    sentiment = sentiment_analysis(cleansed_text)
                    st.write(f"📊 Sentiment: {sentiment.capitalize()}")
                    insert_comment(st.session_state.username, comment, sentiment, "Unknown", "Unknown", "Unknown", "Unknown")
                    st.success("✅ Voice note submitted successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                os.remove(filename)

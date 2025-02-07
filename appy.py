import streamlit as st
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
import io
import wave
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from analysis import clean_text, tokenize_and_filter, analyze_emotions, sentiment_analysis, plot_emotions
from database import (
    create_users_table, insert_user, authenticate_user,
    reset_password, check_user_exists, create_comments_table, insert_comment
)

# Create database tables
create_users_table()
create_comments_table()

# Session state variables
if 'page' not in st.session_state:
    st.session_state.page = "Login"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'audio_buffer' not in st.session_state:
    st.session_state.audio_buffer = None

# Custom CSS for styling
st.markdown("""
    <style>
    .stButton button { background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px 20px; font-size: 16px; }
    .stButton button:hover { background-color: #45a049; }
    .stTextInput input { border-radius: 5px; padding: 10px; font-size: 16px; }
    .stTitle { font-size: 36px; font-weight: bold; color: #2E86C1; }
    .stSubheader { font-size: 24px; color: #2E86C1; }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Authentication Pages
# ----------------------------
if st.session_state.page == "Login":
    st.markdown("<div class='stTitle'>Login</div>", unsafe_allow_html=True)
    username = st.text_input('Username', placeholder="Enter your username")
    password = st.text_input('Password', type='password', placeholder="Enter your password")
    
    if st.button("Login"):
        if username and password and authenticate_user(username, password):
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
        if username and password and email and not check_user_exists(username):
            insert_user(username, password, email)
            st.success("User registered successfully! Please login.")
            st.session_state.page = "Login"
        else:
            st.error("Please fill all fields or choose a different username.")

elif st.session_state.page == "Reset Password":
    st.markdown("<div class='stTitle'>Reset Password</div>", unsafe_allow_html=True)
    username = st.text_input('Username')
    new_password = st.text_input('New Password', type='password')
    
    if st.button("Reset Password"):
        if username and new_password:
            reset_password(username, new_password)
            st.success("Password reset successfully! Please login.")
            st.session_state.page = "Login"
        else:
            st.error("Please provide all details.")

# ----------------------------
# Home Page – Voice Analysis
# ----------------------------
elif st.session_state.page == "Home":
    st.markdown(f"<div class='stTitle'>Welcome, {st.session_state.username}!</div>", unsafe_allow_html=True)
    st.markdown("<div class='stSubheader'>Record your voice note for sentiment analysis</div>", unsafe_allow_html=True)
    
    def process_audio(frame: av.AudioFrame) -> np.ndarray:
        return frame.to_ndarray()
    
    if st.button("🎙 Start Recording"):
        st.session_state.recording = True
    
    if st.session_state.recording:
        webrtc_ctx = webrtc_streamer(
            key="speech-to-text",
            mode=WebRtcMode.SENDRECV,
            audio_receiver_size=1024,
            media_stream_constraints={"video": False, "audio": True},
        )
        if webrtc_ctx.audio_receiver:
            audio_frames = []
            while True:
                try:
                    frame = webrtc_ctx.audio_receiver.get_frame(timeout=1)
                    audio_frames.append(process_audio(frame))
                except:
                    break
            if audio_frames:
                audio_data = np.concatenate(audio_frames, axis=0)
                sample_rate = 16000
                audio_buffer = io.BytesIO()
                with wave.open(audio_buffer, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes(audio_data.tobytes())
                audio_buffer.seek(0)
                st.session_state.audio_buffer = audio_buffer
                st.audio(audio_buffer, format="audio/wav")
    
    if st.button("🛑 Stop Recording"):
        st.session_state.recording = False
    
    if st.session_state.audio_buffer and st.button("📤 Analyze Audio"):
        recognizer = sr.Recognizer()
        with sr.AudioFile(st.session_state.audio_buffer) as source:
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
            st.error("❌ Speech Recognition could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"❌ Could not request results from Speech Recognition service: {e}")

elif st.session_state.page == "About Us":
    st.markdown("<div class='stTitle'>About Us</div>", unsafe_allow_html=True)
    st.write("""### 🎤 Voice Sentiment Analysis\nThis tool helps users assess their stress levels by analyzing voice input.""")

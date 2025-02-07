import streamlit as st
import speech_recognition as sr
import os

# Initialize users in session state
if 'users' not in st.session_state:
    st.session_state['users'] = {}

if 'page' not in st.session_state:
    st.session_state.page = "Login"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# Functions
def authenticate_user(username, password):
    return username in st.session_state['users'] and st.session_state['users'][username] == password

def register_user(username, password, email):
    if username in st.session_state['users']:
        return False
    st.session_state['users'][username] = password
    return True

def reset_password(username, new_password):
    if username in st.session_state['users']:
        st.session_state['users'][username] = new_password
        return True
    return False

def sentiment_analysis(text):
    if "happy" in text or "good" in text:
        return "Positive"
    elif "sad" in text or "bad" in text:
        return "Negative"
    else:
        return "Neutral"

# --- UI Components ---
st.markdown(
    """
    <style>
    .stButton button { background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px 20px; font-size: 16px; }
    .stTextInput input { border-radius: 5px; padding: 10px; font-size: 16px; }
    .stTitle { font-size: 36px; font-weight: bold; color: #2E86C1; }
    .stSubheader { font-size: 24px; color: #2E86C1; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Navigation ---
if st.session_state.logged_in:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🏠 Home"):
            st.session_state.page = "Home"
    with col2:
        if st.button("ℹ️ About Us"):
            st.session_state.page = "About Us"
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.page = "Login"
            st.rerun()

# --- Login Page ---
if st.session_state.page == "Login":
    st.markdown("<div class='stTitle'>Login</div>", unsafe_allow_html=True)
    username = st.text_input('Username', placeholder="Enter your username")
    password = st.text_input('Password', type='password', placeholder="Enter your password")

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

    if st.button("Forgot Password?"):
        st.session_state.page = "Forgot Password"
        st.rerun()

# --- Registration Page ---
elif st.session_state.page == "Register":
    st.markdown("<div class='stTitle'>Register</div>", unsafe_allow_html=True)
    new_username = st.text_input('New Username', placeholder="Choose a username")
    new_email = st.text_input('Email', placeholder="Enter your email")
    new_password = st.text_input('New Password', type='password', placeholder="Choose a password")

    if st.button("Sign Up"):
        if new_username and new_password and new_email:
            if register_user(new_username, new_password, new_email):
                st.success("✅ Registration successful! Please log in.")
                st.session_state.page = "Login"
                st.rerun()
            else:
                st.error("❌ Username already exists. Try another.")
        else:
            st.error("❌ All fields are required!")

    if st.button("Back to Login"):
        st.session_state.page = "Login"
        st.rerun()

# --- Password Reset Page ---
elif st.session_state.page == "Forgot Password":
    st.markdown("<div class='stTitle'>Reset Password</div>", unsafe_allow_html=True)
    reset_username = st.text_input('Username', placeholder="Enter your username")
    new_password = st.text_input('New Password', type='password', placeholder="Enter a new password")

    if st.button("Reset Password"):
        if reset_password(reset_username, new_password):
            st.success("✅ Password reset successful! Please log in.")
            st.session_state.page = "Login"
            st.rerun()
        else:
            st.error("❌ Username not found.")

    if st.button("Back to Login"):
        st.session_state.page = "Login"
        st.rerun()

# --- Home Page ---
elif st.session_state.page == "Home":
    st.markdown(f"<div class='stTitle'>Welcome, {st.session_state.username}!</div>", unsafe_allow_html=True)
    st.markdown("<div class='stSubheader'>Upload an Audio File for Sentiment Analysis</div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📤 Upload an audio file", type=["wav", "mp3"])

    if uploaded_file:
        st.audio(uploaded_file, format="audio/wav")
        recognizer = sr.Recognizer()
        with sr.AudioFile(uploaded_file) as source:
            audio_data = recognizer.record(source)
        try:
            comment = recognizer.recognize_google(audio_data)
            st.write("🗣️ You said:", comment)
            sentiment = sentiment_analysis(comment)
            st.write(f"📊 Sentiment: {sentiment}")
            st.success("✅ Analysis complete!")
        except sr.UnknownValueError:
            st.error("❌ Could not understand audio.")
        except sr.RequestError as e:
            st.error(f"❌ Speech Recognition service error: {e}")

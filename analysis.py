import string
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def clean_text(text):
    lower_case = text.lower()
    cleansed_text = lower_case.translate(str.maketrans('', '', string.punctuation))
    return cleansed_text


def tokenize_and_filter(text):
    tokenize_words = word_tokenize(text, "english")
    final_words = [word for word in tokenize_words if word not in stopwords.words("english")]
    return final_words


def analyze_emotions(final_words):
    """
    Analyze emotions based on the final words.
    """
    emotion_list = []
    try:
        with open('farmer_emotions.txt', 'r') as file:
            for line in file:
                try:
                    # Split the line into word and emotion
                    word, emotion = line.strip().split(':', 1)  # Split on the first colon only
                    if word in final_words:
                        emotion_list.append(emotion)
                except ValueError:
                    # Skip lines that don't have the expected format
                    continue
    except FileNotFoundError:
        st.error("❌ Emotion lexicon file 'farmer_emotions.txt' not found.")
        return {}

    emotion_counts = Counter(emotion_list)
    return emotion_counts


def sentiment_analysis(text):
    score = SentimentIntensityAnalyzer().polarity_scores(text)
    neg = score['neg']
    pos = score['pos']

    if neg > pos:
        return "High Stress"
    elif pos > neg:
        return "Low Stress"
    else:
        return "Neutral Stress Level"


def plot_emotions(emotion_counts):
    fig, ax = plt.subplots()
    ax.bar(emotion_counts.keys(), emotion_counts.values())
    fig.autofmt_xdate()
    return fig

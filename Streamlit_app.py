import streamlit as st
import requests
import re
import nltk # Standard for word detection
from nltk.corpus import words

# Setup: Download dictionary if not present
try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')
    
word_list = set(words.words())

st.title("Max-Stride Explorer (Stride 5000)")

def colorize_and_preserve(sequence):
    """
    Looks for English words in the sequence. 
    Highlights found words in blue, keeps everything else (including spaces/scrambles).
    """
    # Regex to find sequences of letters
    tokens = re.split(r'([^A-Z])', sequence)
    formatted = []
    
    for token in tokens:
        # If it's a word and in our massive dictionary, make it blue
        if token.lower() in word_list and len(token) > 2:
            formatted.append(f"$\color{{blue}}{{{token.upper()}}}$")
        else:
            formatted.append(token)
    return "".join(formatted)

# UI
target = st.text_input("Target Pattern:").upper()
stride = st.number_input("Stride:", min_value=1, max_value=5000, value=5000)

if st.button("Execute Max-Stride Stream"):
    # Stream logic here
    # 1. Fetch text
    # 2. Extract char every 5000
    # 3. Apply colorize_and_preserve()
    st.markdown(f"**Result Preview:** {colorize_and_preserve(raw_extracted_data)}")

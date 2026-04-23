import streamlit as st
import re
import nltk
from nltk.corpus import words

# Download dictionary for highlighting
@st.cache_resource
def get_word_list():
    nltk.download('words')
    return set(words.words())

word_list = get_word_list()

def colorize_and_group(sequence):
    """
    Groups letters into words, turns dictionary words BLUE,
    and preserves all raw characters (scrambles/spacing).
    """
    # Split by non-alphanumeric to keep punctuation/spaces as is
    tokens = re.split(r'([^a-zA-Z0-9])', sequence)
    formatted = []
    
    for token in tokens:
        # Check if word is in dictionary and highlight
        if token.lower() in word_list and len(token) > 2:
            formatted.append(f"$\color{{blue}}{{{token.upper()}}}$")
        else:
            formatted.append(token)
    return "".join(formatted)

# Inside your Scan Logic (after finding a match):
# Instead of printing raw text, you now pass it through:
# st.markdown(colorize_and_group(found_sequence))

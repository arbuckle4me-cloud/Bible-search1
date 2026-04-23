import streamlit as st
import requests
import re
import nltk
from nltk.corpus import words

# Setup
@st.cache_resource
def get_word_list():
    nltk.download('words', quiet=True)
    return set(words.words())

word_list = get_word_list()

st.title("API-Based ELS Scanner")

# UI Inputs
name_to_search = st.text_input("Name/Pattern to Search:", "CURT STREHLAU").upper()
book_chapter = st.text_input("Bible Book & Chapter (e.g., John 1):", "Genesis 1")
min_stride = st.number_input("Min Stride:", value=1)
max_stride = st.number_input("Max Stride:", value=100)

def colorize(sequence):
    """Highlights dictionary words found in the sequence in blue."""
    tokens = re.split(r'([^a-zA-Z0-9])', sequence)
    formatted = []
    for t in tokens:
        if t.lower() in word_list and len(t) > 2:
            formatted.append(f"$\color{{blue}}{{{t.upper()}}}$")
        else:
            formatted.append(t)
    return "".join(formatted)

if st.button("Scan API Data"):
    # API Call
    url = f"https://bible-api.com/{book_chapter}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        full_text = data['text'].upper()
        clean_text = re.sub(r'[^A-Z]', '', full_text)
        name = name_to_search.replace(" ", "")
        
        st.write(f"Scanning {book_chapter}...")
        
        found = False
        first_char = name[0]
        for start in [m.start() for m in re.finditer(first_char, clean_text)]:
            for stride in range(min_stride, max_stride + 1):
                if start + (len(name) * stride) >= len(clean_text):
                    break
                
                match = True
                for idx, char in enumerate(name):
                    if clean_text[start + (idx * stride)] != char:
                        match = False
                        break
                
                if match:
                    found = True
                    st.success(f"MATCH: {name_to_search} at Stride {stride}")
                    st.markdown(colorize(clean_text[start : start + (len(name)*stride)]))
        
        if not found:
            st.warning("No ELS match found in this chapter with current settings.")
    else:
        st.error("Could not reach Bible API. Check your book/chapter format.")

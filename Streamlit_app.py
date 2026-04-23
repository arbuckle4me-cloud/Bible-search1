import streamlit as st
import requests
import re
import nltk
from nltk.corpus import words

# Initialize dictionary
@st.cache_resource
def download_nltk():
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words')
    return set(words.words())

word_list = download_nltk()

st.title("Max-Stride Word-Aware Streamer")

def colorize_sequence(sequence):
    # Use regex to find alphanumeric tokens while preserving separators
    tokens = re.split(r'([^a-zA-Z0-9])', sequence)
    formatted = []
    for token in tokens:
        # If token is in dictionary and longer than 2 chars, make it blue
        if token.lower() in word_list and len(token) > 2:
            formatted.append(f"$\color{{blue}}{{{token.upper()}}}$")
        else:
            formatted.append(token)
    return "".join(formatted)

# UI Elements
urls_input = st.text_area("Enter URL list (one per line):")
target = st.text_input("Target Pattern (e.g., THE):").upper()
stride = st.number_input("Stride:", min_value=1, max_value=5000, value=5000)

if st.button("Execute Stream"):
    url_list = urls_input.split('\n')
    for url in url_list:
        url = url.strip()
        if not url: continue
        
        st.write(f"--- Processing: {url} ---")
        try:
            with requests.get(url, stream=True, timeout=15) as r:
                content = r.text.upper()
                
                # Logic to find matches and stream every Nth character
                # We find the index where the pattern starts
                for match in re.finditer(re.escape(target), content):
                    start = match.start()
                    
                    # Capture sequence from start, jumping by stride
                    extracted = ""
                    # Grab a window of characters to analyze
                    for i in range(start, min(start + (2000 * stride), len(content)), stride):
                        extracted += content[i]
                    
                    # Apply color formatting
                    final_output = colorize_sequence(extracted)
                    
                    st.markdown(f"**Match at index {start}:**")
                    st.markdown(final_output)
                    
        except Exception as e:
            st.error(f"Error: {e}")

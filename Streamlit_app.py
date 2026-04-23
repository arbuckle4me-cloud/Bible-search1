import streamlit as st
import requests
import re
import nltk
from nltk.corpus import words
from bs4 import BeautifulSoup

# Setup
@st.cache_resource
def get_word_list():
    nltk.download('words')
    return set(words.words())

word_list = get_word_list()

st.title("Universal ELS Scanner")

# UI
roots = st.text_area("Root URLs (one per line):", "https://www.gutenberg.org/ebooks/subject/7")
name_to_search = st.text_input("Name to search (e.g., CURT STREHLAU):").upper()
min_stride = st.number_input("Min Stride:", value=1)
max_stride = st.number_input("Max Stride:", value=5000)

def colorize(sequence):
    tokens = re.split(r'([^a-zA-Z0-9])', sequence)
    formatted = []
    for t in tokens:
        if t.lower() in word_list and len(t) > 2:
            formatted.append(f"$\color{{blue}}{{{t.upper()}}}$")
        else:
            formatted.append(t)
    return "".join(formatted)

if st.button("Execute Full Scan"):
    # Crawler Logic
    response = requests.get(roots.strip())
    soup = BeautifulSoup(response.text, 'html.parser')
    links = ["https://www.gutenberg.org" + a['href'] for a in soup.find_all('a', href=re.compile(r'\.txt$'))]
    
    progress = st.progress(0)
    for i, link in enumerate(links):
        st.write(f"Scanning: {link}")
        try:
            text = requests.get(link).text.upper()
            clean_text = re.sub(r'[^A-Z]', '', text)
            
            # ELS Search Logic
            name = name_to_search.replace(" ", "")
            for stride in range(min_stride, max_stride + 1):
                for start in range(len(clean_text) - (len(name) * stride)):
                    match = True
                    for idx, char in enumerate(name):
                        if clean_text[start + (idx * stride)] != char:
                            match = False; break
                    if match:
                        st.success(f"MATCH: {name} at Stride {stride}")
                        st.markdown(colorize(clean_text[start : start + (len(name)*stride)]))
        except Exception as e:
            st.error(f"Failed: {link}")
        progress.progress((i + 1) / len(links))

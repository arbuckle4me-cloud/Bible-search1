import streamlit as st
import requests
import re
import nltk
from nltk.corpus import words
from bs4 import BeautifulSoup

# Setup: Download dictionary once
@st.cache_resource
def get_word_list():
    nltk.download('words', quiet=True)
    return set(words.words())

word_list = get_word_list()

st.title("Universal ELS Name & Pattern Hunter")

# Inputs
roots = st.text_area("Root URLs to scan (one per line):", 
                     "https://www.gutenberg.org/ebooks/search/?query=bible\nhttps://www.gutenberg.org/ebooks/subject/7")
name_to_search = st.text_input("Name/Pattern to Search:", "CURT STREHLAU").upper()
min_stride = st.number_input("Min Stride:", value=1)
max_stride = st.number_input("Max Stride:", value=5000)

def colorize(sequence):
    """Groups text into words and highlights dictionary words in blue."""
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
    all_links = []
    for root in roots.split('\n'):
        try:
            response = requests.get(root.strip(), timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = ["https://www.gutenberg.org" + a['href'] for a in soup.find_all('a', href=re.compile(r'\.txt$'))]
            all_links.extend(links)
        except:
            st.error(f"Could not reach {root}")
    
    st.write(f"Total files found: {len(all_links)}")
    progress = st.progress(0)
    
    # Optimized Scan
    for i, link in enumerate(all_links):
        try:
            text = requests.get(link, timeout=5).text.upper()
            clean_text = re.sub(r'[^A-Z]', '', text)
            name = name_to_search.replace(" ", "")
            
            # Jump to occurrences of the first letter
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
                        st.success(f"MATCH FOUND: {name_to_search} at Stride {stride} in {link}")
                        st.markdown(colorize(clean_text[start : start + (len(name)*stride)]))
        except:
            continue
        progress.progress((i + 1) / len(all_links))

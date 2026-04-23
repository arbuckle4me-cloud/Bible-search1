import streamlit as st
import requests
import re
import nltk
from nltk.corpus import words
from bs4 import BeautifulSoup

# Setup
@st.cache_resource
def get_word_list():
    nltk.download('words', quiet=True)
    return set(words.words())

word_list = get_word_list()

st.title("Universal ELS Archive Scanner")

# Pre-populated sources
default_sources = (
    "https://www.gutenberg.org/ebooks/search/?query=bible\n"
    "https://www.gutenberg.org/ebooks/search/?query=quran\n"
    "https://www.gutenberg.org/ebooks/search/?query=enoch\n"
    "https://www.gutenberg.org/ebooks/search/?query=jubilees"
)

name_to_search = st.text_input("Name/Pattern:", "CURT STREHLAU").upper().replace(" ", "")
sources = st.text_area("Source URLs (Gutenberg Search Pages):", default_sources, height=150)
min_stride = st.number_input("Min Stride:", value=1)
max_stride = st.number_input("Max Stride:", value=500)

results_log = []

def colorize(sequence):
    tokens = re.split(r'([^a-zA-Z0-9])', sequence)
    formatted = []
    for t in tokens:
        if t.lower() in word_list and len(t) > 2:
            formatted.append(f"$\color{{blue}}{{{t.upper()}}}$")
        else:
            formatted.append(t)
    return "".join(formatted)

if st.button("Scan All Sources & Save Results"):
    links = []
    for root in sources.split('\n'):
        try:
            soup = BeautifulSoup(requests.get(root.strip(), timeout=10).text, 'html.parser')
            for a in soup.find_all('a', href=re.compile(r'/ebooks/\d+')):
                if 'txt' in a.get('href', ''): # Simple filter for text files
                    links.append("https://www.gutenberg.org" + a['href'])
        except: continue
    
    st.write(f"Scanning {len(links)} documents...")
    
    for link in links:
        try:
            text = requests.get(link, timeout=10).text.upper()
            clean_text = re.sub(r'[^A-Z]', '', text)
            
            for start in [m.start() for m in re.finditer(name_to_search[0], clean_text)]:
                for stride in range(min_stride, max_stride + 1):
                    match = True
                    for idx, char in enumerate(name_to_search):
                        pos = start + (idx * stride)
                        if pos >= len(clean_text) or clean_text[pos] != char:
                            match = False; break
                    
                    if match:
                        result_str = f"Match in {link} at stride {stride}\nSequence: {clean_text[start : start + (len(name_to_search)*stride)]}"
                        st.success(f"Match found!")
                        st.markdown(colorize(clean_text[start : start + (len(name_to_search)*stride)]))
                        results_log.append(result_str)
        except: continue

    # File Download
    if results_log:
        full_report = "\n\n---\n\n".join(results_log)
        st.download_button(
            label="Download Results as Text File",
            data=full_report,
            file_name="ELS_Results.txt",
            mime="text/plain"
        )
    else:
        st.warning("No matches found.")

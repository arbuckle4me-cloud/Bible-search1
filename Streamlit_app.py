import streamlit as st
import requests
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import nltk

# Setup for blue highlights
@st.cache_resource
def get_word_list():
    nltk.download('words', quiet=True)
    return set(nltk.corpus.words.words())

word_list = get_word_list()

st.title("Universal ELS Archive Scanner (Refined)")

# Inputs
name_to_search = st.text_input("Name to search:", "CURT STREHLAU").upper().replace(" ", "")
max_stride_input = st.number_input("Max Stride Limit:", value=5000)
sources_input = st.text_area("URLs:", "https://www.gutenberg.org/ebooks/search/?query=bible\nhttps://www.gutenberg.org/ebooks/search/?query=quran", height=100)

if 'results_log' not in st.session_state:
    st.session_state.results_log = []

def colorize(sequence):
    tokens = re.split(r'([^a-zA-Z0-9])', sequence)
    formatted = []
    for t in tokens:
        if t.lower() in word_list and len(t) > 2:
            formatted.append(f"$\color{{blue}}{{{t.upper()}}}$")
        else:
            formatted.append(t)
    return "".join(formatted)

col1, col2 = st.columns(2)

with col1:
    if st.button("START SCAN"):
        st.session_state.results_log = []
        urls = [line.strip() for line in sources_input.split('\n') if line.strip()]
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        status_placeholder = st.empty()
        
        for url in urls:
            try:
                soup = BeautifulSoup(requests.get(url, headers=headers, timeout=20).text, 'html.parser')
                for a in soup.find_all('a', href=re.compile(r'/ebooks/\d+')):
                    book_link = urljoin("https://www.gutenberg.org", a['href'])
                    status_placeholder.text(f"Checking: {book_link.split('/')[-1]}")
                    
                    page = requests.get(book_link, headers=headers, timeout=15)
                    txt_match = re.search(r'href="(.*?\.txt)"', page.text)
                    
                    if txt_match:
                        txt_url = urljoin("https://www.gutenberg.org", txt_match.group(1))
                        time.sleep(1)
                        text_content = re.sub(r'[^A-Z]', '', requests.get(txt_url, headers=headers, timeout=20).text.upper())
                        
                        for start in [m.start() for m in re.finditer(name_to_search[0], text_content)]:
                            for stride in range(1, max_stride_input + 1):
                                match = True
                                for idx, char in enumerate(name_to_search):
                                    pos = start + (idx * stride)
                                    if pos >= len(text_content) or text_content[pos] != char:
                                        match = False; break
                                if match:
                                    seq = text_content[start : start + (len(name_to_search)*stride)]
                                    entry = f"Found: {txt_url} (Stride {stride})"
                                    st.session_state.results_log.append(entry + f"\nSequence: {seq}")
                                    st.write(entry)
                                    st.markdown(colorize(seq))
            except Exception as e: st.error(f"Error: {e}")

with col2:
    if st.session_state.results_log:
        file_name = st.text_input("Filename:", "ELS_Results.txt")
        st.download_button("DOWNLOAD RESULTS", data="\n\n".join(st.session_state.results_log), file_name=file_name)

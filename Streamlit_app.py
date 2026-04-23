import streamlit as st
import requests
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import nltk

@st.cache_resource
def get_word_list():
    nltk.download('words', quiet=True)
    return set(nltk.corpus.words.words())

word_list = get_word_list()

st.title("Advanced ELS Matrix Scanner")

# Core Inputs
# Default name removed to empty string
name_to_search = st.text_input("Target Pattern:", "").upper().replace(" ", "")
max_stride_input = st.number_input("Max Stride Limit:", value=5000, min_value=1)

# Bible collection restored and expanded
default_urls = (
    "https://www.gutenberg.org/ebooks/search/?query=bible\n"
    "https://www.gutenberg.org/ebooks/search/?query=holy+bible\n"
    "https://www.gutenberg.org/ebooks/search/?query=quran\n"
    "https://www.gutenberg.org/ebooks/search/?query=enoch"
)
sources_input = st.text_area("Source URLs:", default_urls, height=100)

# Memory State
if 'results_log' not in st.session_state:
    st.session_state.results_log = []

col1, col2 = st.columns(2)

def colorize_sequence(sequence):
    words = re.findall(r'[A-Z]{3,}', sequence)
    formatted_seq = sequence
    for w in sorted(set(words), key=len, reverse=True):
        if w.lower() in word_list:
            formatted_seq = formatted_seq.replace(w, f"$\color{{blue}}{{{w}}}$")
    return formatted_seq

with col1:
    if st.button("EXECUTE SCAN"):
        st.session_state.results_log = [] 
        if not name_to_search:
            st.error("Please enter a target pattern.")
        else:
            urls = [line.strip() for line in sources_input.split('\n') if line.strip()]
            headers = {'User-Agent': 'Mozilla/5.0'}
            status_text = st.empty()
            
            for url in urls:
                try:
                    soup = BeautifulSoup(requests.get(url, headers=headers, timeout=20).text, 'html.parser')
                    book_links = soup.find_all('a', href=re.compile(r'/ebooks/\d+'))
                    
                    for i, a in enumerate(book_links):
                        book_link = urljoin("https://www.gutenberg.org", a['href'])
                        status_text.text(f"Scanning Book {i+1}/{len(book_links)}: {book_link.split('/')[-1]}")
                        
                        page = requests.get(book_link, headers=headers, timeout=15)
                        txt_match = re.search(r'href="(.*?\.txt)"', page.text)
                        
                        if txt_match:
                            txt_url = urljoin("https://www.gutenberg.org", txt_match.group(1))
                            time.sleep(1)
                            raw_text = requests.get(txt_url, headers=headers, timeout=20).text.upper()
                            clean_text = re.sub(r'[^A-Z]', '', raw_text)
                            
                            for start in [m.start() for m in re.finditer(name_to_search[0], clean_text)]:
                                for stride in range(1, max_stride_input + 1):
                                    match = True
                                    for idx, char in enumerate(name_to_search):
                                        pos = start + (idx * stride)
                                        if pos >= len(clean_text) or clean_text[pos] != char:
                                            match = False
                                            break
                                    
                                    if match:
                                        phase_start = start % stride
                                        full_sequence = clean_text[phase_start::stride]
                                        
                                        header_info = f"Target matched in {txt_url.split('/')[-1]} | Stride: {stride} | Phase Offset: {phase_start}"
                                        st.write(f"### {header_info}")
                                        st.markdown(colorize_sequence(full_sequence))
                                        
                                        st.session_state.results_log.append(f"{header_info}\n\n{full_sequence}\n")

                except Exception as e:
                    st.error(f"Network Fault at {url}: {e}")
                    
            status_text.text("Scan Complete.")

with col2:
    if st.session_state.results_log:
        file_name_input = st.text_input("Save Output As:", "ELS_Master_Log.txt")
        st.download_button(
            label="DOWNLOAD TEXT LOG",
            data="\n\n---\n\n".join(st.session_state.results_log),
            file_name=file_name_input,
            mime="text/plain"
        )
    else:
        st.info("Awaiting structural match to enable download.")

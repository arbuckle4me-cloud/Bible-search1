import streamlit as st
import requests
import re
import nltk
from bs4 import BeautifulSoup

# Setup
@st.cache_resource
def get_word_list():
    nltk.download('words', quiet=True)
    return set(nltk.corpus.words.words())

word_list = get_word_list()

st.title("Universal ELS Archive Scanner")

# Inputs
name_to_search = st.text_input("Name/Pattern:", "CURT STREHLAU").upper().replace(" ", "")
default_sources = (
    "https://www.gutenberg.org/ebooks/search/?query=bible\n"
    "https://www.gutenberg.org/ebooks/search/?query=quran\n"
    "https://www.gutenberg.org/ebooks/search/?query=enoch"
)
sources_input = st.text_area("Full Source URLs (Gutenberg):", default_sources, height=150)
file_name_input = st.text_input("Filename for export:", "ELS_Results.txt")
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
    urls = [line.strip() for line in sources_input.split('\n') if line.strip().startswith('http')]
    links = []
    
    # Discovery Phase
    status_text = st.empty()
    status_text.text("Discovering books...")
    for root in urls:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(root, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            for a in soup.find_all('a', href=re.compile(r'/ebooks/\d+')):
                book_url = "https://www.gutenberg.org" + a['href']
                book_page = requests.get(book_url, headers=headers, timeout=10)
                txt_match = re.search(r'href="(.*\.txt)"', book_page.text)
                if txt_match:
                    links.append(txt_match.group(1))
        except: continue
    
    # Scanning Phase
    progress_bar = st.progress(0)
    for i, link in enumerate(links):
        status_text.text(f"Scanning book {i+1} of {len(links)}: {link.split('/')[-1]}")
        progress_bar.progress((i + 1) / len(links))
        
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
                        seq = clean_text[start : start + (len(name_to_search)*stride)]
                        result_str = f"Link: {link} | Stride: {stride}\nSequence: {seq}"
                        st.markdown(f"**Match Found!**")
                        st.markdown(colorize(seq))
                        results_log.append(result_str)
        except: continue

    # Export Phase
    if results_log:
        full_report = "\n\n---\n\n".join(results_log)
        st.download_button(
            label="Download Results as File",
            data=full_report,
            file_name=file_name_input,
            mime="text/plain"
        )
    else:
        st.warning("No matches found.")

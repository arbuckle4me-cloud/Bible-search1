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
sources_input = st.text_area("Full Source URLs:", 
    "https://www.gutenberg.org/ebooks/search/?query=bible\n"
    "https://www.gutenberg.org/ebooks/search/?query=quran", height=100)

# Use session state to store results so they don't vanish
if 'results_log' not in st.session_state:
    st.session_state.results_log = []

# Separate columns for better UI control
col1, col2 = st.columns(2)

with col1:
    if st.button("Start Scan"):
        st.session_state.results_log = [] # Reset on new scan
        urls = [line.strip() for line in sources_input.split('\n') if line.strip()]
        
        status_text = st.empty()
        for root in urls:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(root, headers=headers, timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')
                links = ["https://www.gutenberg.org" + a['href'] for a in soup.find_all('a', href=re.compile(r'/ebooks/\d+'))]
                
                for link in links:
                    status_text.text(f"Scanning: {link.split('/')[-1]}")
                    book_page = requests.get(link, headers=headers, timeout=15)
                    txt_match = re.search(r'href="(.*\.txt)"', book_page.text)
                    if txt_match:
                        txt_url = txt_match.group(1)
                        text = requests.get(txt_url, timeout=15).text.upper()
                        clean_text = re.sub(r'[^A-Z]', '', text)
                        
                        # ELS Logic
                        for start in [m.start() for m in re.finditer(name_to_search[0], clean_text)]:
                            for stride in range(1, 500):
                                match = True
                                for idx, char in enumerate(name_to_search):
                                    pos = start + (idx * stride)
                                    if pos >= len(clean_text) or clean_text[pos] != char:
                                        match = False; break
                                if match:
                                    res = f"Found in {txt_url} (Stride {stride})"
                                    st.session_state.results_log.append(res)
                                    st.write(res)
            except Exception as e:
                st.write(f"Error scanning {root}: {e}")

with col2:
    if st.session_state.results_log:
        file_name = st.text_input("Filename:", "ELS_Results.txt")
        st.download_button(
            label="Download Results",
            data="\n".join(st.session_state.results_log),
            file_name=file_name,
            mime="text/plain"
        )
    else:
        st.info("Scan to see download options.")

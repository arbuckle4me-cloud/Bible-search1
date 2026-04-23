import streamlit as st
import requests
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

st.title("Universal ELS Archive Scanner (Full)")

# UI Inputs
name_to_search = st.text_input("Name to search:", "CURT STREHLAU").upper().replace(" ", "")
sources_input = st.text_area("URLs:", 
    "https://www.gutenberg.org/ebooks/search/?query=bible\n"
    "https://www.gutenberg.org/ebooks/search/?query=quran", height=100)

if 'results_log' not in st.session_state:
    st.session_state.results_log = []

col1, col2 = st.columns(2)

with col1:
    if st.button("START SCAN"):
        st.session_state.results_log = []
        urls = [line.strip() for line in sources_input.split('\n') if line.strip()]
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        
        status_placeholder = st.empty()
        
        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=20)
                soup = BeautifulSoup(response.text, 'html.parser')
                # Find all book links
                book_anchors = soup.find_all('a', href=re.compile(r'/ebooks/\d+'))
                
                for a in book_anchors:
                    book_link = urljoin("https://www.gutenberg.org", a['href'])
                    status_placeholder.text(f"Checking: {book_link.split('/')[-1]}")
                    
                    # Get the actual .txt file link
                    page = requests.get(book_link, headers=headers, timeout=15)
                    txt_match = re.search(r'href="(.*?\.txt)"', page.text)
                    
                    if txt_match:
                        txt_url = urljoin("https://www.gutenberg.org", txt_match.group(1))
                        time.sleep(1) # Crucial: don't hammer the server
                        
                        text_content = requests.get(txt_url, headers=headers, timeout=20).text.upper()
                        clean_text = re.sub(r'[^A-Z]', '', text_content)
                        
                        # ELS Search (Stride 1 to 5000)
                        for start in [m.start() for m in re.finditer(name_to_search[0], clean_text)]:
                            for stride in range(1, 5001):
                                match = True
                                for idx, char in enumerate(name_to_search):
                                    pos = start + (idx * stride)
                                    if pos >= len(clean_text) or clean_text[pos] != char:
                                        match = False; break
                                if match:
                                    entry = f"Found in {txt_url} (Stride {stride})"
                                    st.session_state.results_log.append(entry)
                                    st.write(entry)
            except Exception as e:
                st.error(f"Skipped {url}: {e}")

with col2:
    if st.session_state.results_log:
        file_name = st.text_input("Filename:", "ELS_Results.txt")
        st.download_button(
            label="DOWNLOAD RESULTS",
            data="\n".join(st.session_state.results_log),
            file_name=file_name,
            mime="text/plain"
        )
    else:
        st.info("Run a scan to see download options.")

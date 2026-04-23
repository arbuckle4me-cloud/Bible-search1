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

st.title("Advanced ELS Matrix Scanner (Unlimited)")

name_to_search = st.text_input("Target Pattern:", "").upper().replace(" ", "")
max_stride_input = st.number_input("Max Stride Limit:", value=5000, min_value=1)
sources_input = st.text_area("Source URLs:", 
    "https://www.gutenberg.org/ebooks/search/?query=bible\n"
    "https://www.gutenberg.org/ebooks/search/?query=quran\n"
    "https://www.gutenberg.org/ebooks/search/?query=enoch", height=100)

if 'results_log' not in st.session_state:
    st.session_state.results_log = []

def colorize_sequence(sequence):
    words = re.findall(r'[A-Z]{3,}', sequence)
    formatted_seq = sequence
    for w in sorted(set(words), key=len, reverse=True):
        if w.lower() in word_list:
            formatted_seq = formatted_seq.replace(w, f"$\color{{blue}}{{{w}}}$")
    return formatted_seq

with st.expander("SCANNER"):
    if st.button("EXECUTE FULL ARCHIVE SCAN"):
        st.session_state.results_log = [] 
        urls = [line.strip() for line in sources_input.split('\n') if line.strip()]
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        for base_url in urls:
            next_url = base_url
            while next_url:
                response = requests.get(next_url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Process all books on current page
                book_links = soup.find_all('a', href=re.compile(r'/ebooks/\d+'))
                for a in book_links:
                    book_link = urljoin("https://www.gutenberg.org", a['href'])
                    page = requests.get(book_link, headers=headers)
                    txt_match = re.search(r'href="(.*?\.txt)"', page.text)
                    
                    if txt_match:
                        txt_url = urljoin("https://www.gutenberg.org", txt_match.group(1))
                        time.sleep(0.5)
                        clean_text = re.sub(r'[^A-Z]', '', requests.get(txt_url, headers=headers).text.upper())
                        
                        for start in [m.start() for m in re.finditer(name_to_search[0], clean_text)]:
                            for stride in range(1, max_stride_input + 1):
                                # ... (Scan logic remains same) ...
                                if all(clean_text[start + (idx * stride)] == char 
                                       for idx, char in enumerate(name_to_search)):
                                    phase_start = start % stride
                                    full_sequence = clean_text[phase_start::stride]
                                    st.markdown(f"**Found in {txt_url.split('/')[-1]} | Stride: {stride}**")
                                    st.markdown(colorize_sequence(full_sequence))
                                    st.session_state.results_log.append(f"{txt_url}\n{full_sequence}")

                # Check for "Next" page
                next_tag = soup.find('a', string="Next")
                next_url = urljoin("https://www.gutenberg.org/ebooks/", next_tag['href']) if next_tag else None

if st.session_state.results_log:
    st.download_button("DOWNLOAD RESULTS", "\n\n".join(st.session_state.results_log), "Results.txt")

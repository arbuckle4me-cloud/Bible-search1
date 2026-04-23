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

# Pre-populated full URLs for reliability
default_sources = (
    "https://www.gutenberg.org/ebooks/search/?query=King+James+Bible\n"
    "https://www.gutenberg.org/ebooks/search/?query=Quran\n"
    "https://www.gutenberg.org/ebooks/search/?query=Enoch\n"
    "https://www.gutenberg.org/ebooks/search/?query=Jubilees"
)

name_to_search = st.text_input("Name/Pattern:", "CURT STREHLAU").upper().replace(" ", "")
sources_input = st.text_area("Full Source URLs (Gutenberg):", default_sources, height=200)
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
    # Clean the input to ignore empty lines or accidental breaks
    urls = [line.strip() for line in sources_input.split('\n') if line.strip().startswith('http')]
    
    links = []
    for root in urls:
        try:
            # Add headers to avoid being blocked
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(root, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract links to raw text files
            for a in soup.find_all('a', href=re.compile(r'/ebooks/\d+')):
                book_url = "https://www.gutenberg.org" + a['href']
                # Get the actual .txt file link for that book
                book_page = requests.get(book_url, headers=headers, timeout=10)
                txt_match = re.search(r'href="(.*\.txt)"', book_page.text)
                if txt_match:
                    links.append(txt_match.group(1))
        except Exception as e:
            st.warning(f"Skipping a source due to error: {e}")
            continue
    
    st.write(f"Found {len(links)} books. Scanning...")
    
    for link in links:
        try:
            text = requests.get(link, headers=headers, timeout=10).text.upper()
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
        st.warning("No matches found in the selected range.")

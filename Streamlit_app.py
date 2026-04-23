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

st.title("ELS Full-Text Skip Processor")

# Inputs
max_stride_input = st.number_input("Max Stride Limit:", value=5000)
sources_input = st.text_area("URLs:", "https://www.gutenberg.org/ebooks/search/?query=bible", height=100)

def colorize_groups(text):
    # This function looks for word patterns in the extracted ELS sequence
    # and wraps them in blue if they exist in the dictionary
    words = re.findall(r'[A-Z]{3,}', text) # Looks for 3+ letter sequences
    formatted = text
    for word in words:
        if word.lower() in word_list:
            formatted = formatted.replace(word, f"$\color{{blue}}{{{word}}}$")
    return formatted

if st.button("RUN FULL TEXT SCAN"):
    urls = [line.strip() for line in sources_input.split('\n') if line.strip()]
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for url in urls:
        try:
            soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
            for a in soup.find_all('a', href=re.compile(r'/ebooks/\d+')):
                book_link = urljoin("https://www.gutenberg.org", a['href'])
                page = requests.get(book_link, headers=headers)
                txt_match = re.search(r'href="(.*?\.txt)"', page.text)
                
                if txt_match:
                    txt_url = urljoin("https://www.gutenberg.org", txt_match.group(1))
                    text_content = re.sub(r'[^A-Z]', '', requests.get(txt_url).text.upper())
                    
                    st.write(f"--- Processing: {txt_url.split('/')[-1]} ---")
                    
                    # Apply stride to the full text
                    for stride in range(1, max_stride_input + 1):
                        # Construct the skip sequence for the entire text
                        els_sequence = text_content[::stride]
                        
                        # Check if this sequence contains recognizable word groups
                        # We only display if we find something substantial
                        if len(els_sequence) > 10:
                            st.markdown(f"**Stride {stride}:**")
                            st.markdown(colorize_groups(els_sequence))
                            time.sleep(0.1) # Pace the output
        except Exception as e: st.error(f"Error: {e}")

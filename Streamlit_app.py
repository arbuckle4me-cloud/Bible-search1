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

st.title("ELS Full-Text Skip Processor (Final)")

# Inputs
name_to_search = st.text_input("Name/Pattern:", "CURT STREHLAU").upper().replace(" ", "")
max_stride_input = st.number_input("Max Stride Limit:", value=5000)
sources_input = st.text_area("URLs:", "https://www.gutenberg.org/ebooks/search/?query=bible", height=100)

def colorize_groups(text):
    # Extracts the sequence and highlights words from the dictionary in blue
    words = re.findall(r'[A-Z]{3,}', text)
    formatted = text
    for word in words:
        if word.lower() in word_list:
            formatted = formatted.replace(word, f"$\color{{blue}}{{{word}}}$")
    return formatted

if st.button("RUN FULL SCAN"):
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
                    
                    st.write(f"### Analyzing: {txt_url.split('/')[-1]}")
                    
                    # Apply stride to the full text from the start
                    for stride in range(1, max_stride_input + 1):
                        els_sequence = text_content[::stride]
                        
                        # Display if the sequence contains the pattern or recognized words
                        if name_to_search in els_sequence or any(w.upper() in els_sequence for w in list(word_list)[:50]):
                            st.markdown(f"**Stride {stride} Found:**")
                            st.markdown(colorize_groups(els_sequence))
                            st.divider()
        except Exception as e: st.error(f"Error: {e}")

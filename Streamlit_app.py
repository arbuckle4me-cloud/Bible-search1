import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

st.title("EOTC Canon Search Tool")

bible_canon = {
    "Genesis (KJV)": "https://www.gutenberg.org/files/10/10-h/10-h.htm",
    "Book of Enoch": "https://www.gutenberg.org/ebooks/77815.txt.utf-8",
    "Book of Jubilees": "https://sacred-texts.com/bib/jub/jub01.htm"
}

headers = {'User-Agent': 'Mozilla/5.0'}
search_term = st.text_input("Enter your search term:")

# This creates a placeholder where results will appear in real-time
results_placeholder = st.empty()
log_area = st.container()

if st.button("Search"):
    with log_area:
        for book_name, url in bible_canon.items():
            st.write(f"Scanning {book_name}...")
            try:
                response = requests.get(url, headers=headers, timeout=(5, 10))
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    text = soup.get_text()
                    
                    # Search for the term
                    if search_term.lower() in text.lower():
                        # Find the index of the term to grab context
                        start_idx = text.lower().find(search_term.lower())
                        
                        # Grab 50 characters before and after (the "context")
                        context_start = max(0, start_idx - 50)
                        context_end = min(len(text), start_idx + len(search_term) + 50)
                        context = text[context_start:context_end].replace("\n", " ")
                        
                        # Display the match with context in the results area
                        results_placeholder.success(f"MATCH in {book_name}: ...{context}...")
                    
                time.sleep(1) 
            except Exception as e:
                st.error(f"Error in {book_name}")

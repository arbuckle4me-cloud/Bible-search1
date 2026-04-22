import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time

st.title("EOTC Canon Data Hunter")

# Use a clean, reliable dictionary
bible_canon = {
    "Genesis (KJV)": "https://www.gutenberg.org/files/10/10-h/10-h.htm",
    "Enoch": "https://www.ccel.org/c/charles/otpseudepig/enoch/ENOCH_1.HTM",
    "Jubilees": "https://www.pseudepigrapha.com/jubilees/index.htm"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
search_term = st.text_input("Enter your search term:")

# This creates a persistent area that won't be wiped out
results_container = st.container()

def perform_search(term):
    for book_name, url in bible_canon.items():
        # Use a temporary placeholder that gets replaced by the next book
        status = st.empty()
        status.info(f"Scanning {book_name}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                text = soup.get_text()
                
                # Regex: Find term and capture EVERYTHING following it (DOTALL covers newlines)
                pattern = re.compile(rf"{re.escape(term)}(.*)", re.IGNORECASE | re.DOTALL)
                match = pattern.search(text)
                
                if match:
                    # Found it! Display immediately in the persistent container
                    with results_container:
                        st.success(f"MATCH FOUND in {book_name}:")
                        # Capture the full sequence of characters after the term
                        st.code(f"{term} -> {match.group(1)[:300]}...") 
            
            # Clear the scanning message so the next book gets its own slot
            status.empty()
            time.sleep(0.5) 
            
        except Exception as e:
            status.error(f"Failed {book_name}: {e}")

if st.button("Search"):
    if search_term:
        perform_search(search_term)
    else:
        st.warning("Please enter a search term.")

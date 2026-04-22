import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time

st.title("EOTC Canon Data Hunter")

bible_canon = {
    "Genesis (KJV)": "https://www.gutenberg.org/files/10/10-h/10-h.htm",
    "Book of Enoch": "https://www.ccel.org/c/charles/otpseudepig/enoch/ENOCH_1.HTM",
    "Book of Jubilees": "https://www.pseudepigrapha.com/jubilees/index.htm"
}

headers = {'User-Agent': 'Mozilla/5.0'}
search_term = st.text_input("Enter your search term:")

# Container for live results
results_container = st.container()

if st.button("Search"):
    if not search_term:
        st.warning("Please enter a term.")
    else:
        for book_name, url in bible_canon.items():
            status = st.empty()
            status.text(f"Scanning {book_name}...")
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    text = soup.get_text()
                    
                    # REGEX PATTERN:
                    # re.escape ensures the search term isn't treated as regex code
                    # (.*) captures EVERYTHING after the term until the end of the line/string
                    # re.DOTALL ensures it captures even if there are newlines
                    pattern = re.compile(rf"{re.escape(search_term)}(.*)", re.IGNORECASE | re.DOTALL)
                    matches = pattern.findall(text)
                    
                    if matches:
                        with results_container:
                            st.success(f"MATCH FOUND in {book_name}:")
                            for match in matches:
                                # Show the raw string following your search term
                                st.code(f"{search_term} -> {match[:200]}...") # Truncated to 200 chars for readability
                
                status.empty()
                time.sleep(0.5) 
            except Exception as e:
                status.error(f"Could not load {book_name}: {e}")

import streamlit as st
import requests
import re
import time

st.title("EOTC Canon: Safe Search")

# Using 'with' block for connection management to prevent hanging
def get_text_safely(url):
    try:
        # User-Agent is mandatory for academic/archival sites
        headers = {'User-Agent': 'Mozilla/5.0'}
        with requests.get(url, headers=headers, timeout=5) as r:
            if r.status_code == 200:
                return r.text
            return None
    except:
        return None

bible_canon = {
    "Genesis (KJV)": "https://www.gutenberg.org/files/10/10-h/10-h.htm",
    "Enoch": "https://www.ccel.org/c/charles/otpseudepig/enoch/ENOCH_1.HTM",
    "Jubilees": "https://www.pseudepigrapha.com/jubilees/index.htm"
}

search_term = st.text_input("Enter search term:")

if st.button("Start Search"):
    for book, url in bible_canon.items():
        st.write(f"Checking {book}...")
        text = get_text_safely(url)
        
        if text:
            # Look for term + following string
            pattern = re.compile(rf"{re.escape(search_term)}(.*)", re.IGNORECASE | re.DOTALL)
            match = pattern.search(text)
            
            if match:
                st.success(f"Found in {book}:")
                # Showing the first 500 chars after the match
                st.code(match.group(1)[:500])
            else:
                st.write(f"No match in {book}")
        else:
            st.warning(f"Could not reach {book} (Server blocked or slow).")
        
        time.sleep(0.5)

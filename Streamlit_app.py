import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time

st.title("EOTC Canon Data Hunter")

bible_canon = {
    "Genesis (KJV)": "https://www.gutenberg.org/files/10/10-h/10-h.htm",
    "Enoch": "https://www.ccel.org/c/charles/otpseudepig/enoch/ENOCH_1.HTM",
    "Jubilees": "https://www.pseudepigrapha.com/jubilees/index.htm"
}

headers = {'User-Agent': 'Mozilla/5.0'}
search_term = st.text_input("Enter your search term:")

# Container for results
results_container = st.container()

if st.button("Search"):
    if search_term:
        for book_name, url in bible_canon.items():
            # Use st.write to log progress clearly
            st.write(f"--- Scanning {book_name} ---")
            
            try:
                # Tightened timeout for stability
                response = requests.get(url, headers=headers, timeout=8)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    text = soup.get_text()
                    
                    # Regex for term + everything following it
                    pattern = re.compile(rf"{re.escape(search_term)}(.*)", re.IGNORECASE | re.DOTALL)
                    match = pattern.search(text)
                    
                    if match:
                        with results_container:
                            st.success(f"Match in {book_name}:")
                            # Display match and following 500 chars
                            st.code(f"{search_term} -> {match.group(1)[:500]}...")
                    else:
                        st.write(f"No match in {book_name}.")
                else:
                    st.write(f"Could not reach {book_name} (Status: {response.status_code})")
            
            except Exception as e:
                # If one fails, it writes the error but continues the loop
                st.error(f"Error skipping {book_name}: {e}")
                continue 
            
            time.sleep(0.5) 
    else:
        st.warning("Please enter a term.")

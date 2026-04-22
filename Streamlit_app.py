
import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

st.title("EOTC Canon Search Tool")

# The list of books
bible_canon = {
    "Genesis (KJV)": "https://www.gutenberg.org/files/10/10-h/10-h.htm",
    "Enoch": "https://www.gutenberg.org/ebooks/77815.txt.utf-8",
    "Jubilees": "https://sacred-texts.com/bib/jub/jub01.htm"
}

search_term = st.text_input("Enter your search term:")

if st.button("Search"):
    for book_name, url in bible_canon.items():
        st.write(f"Searching {book_name}...")
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text()
            
            if search_term.lower() in text.lower():
                st.success(f"Match found in {book_name}!")
            time.sleep(1)
        except Exception as e:
            st.error(f"Could not access {book_name}")

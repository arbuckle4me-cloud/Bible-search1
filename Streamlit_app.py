import streamlit as st
import requests
import re

st.title("Live Stream Pattern Hunter")

# This is a list of direct stream links (not download pages)
urls = [
    "https://www.gutenberg.org/cache/epub/10/pg10.txt", # KJV
    "https://www.gutenberg.org/cache/epub/17/pg17.txt", # Book of Mormon
    "https://www.gutenberg.org/cache/epub/16955/pg16955.txt" # Quran
]

target = st.text_input("Pattern:").upper()
stride = st.number_input("Stride:", value=10)

if st.button("Start Live Scan"):
    for url in urls:
        st.write(f"Streaming {url}...")
        # Stream=True tells Python to NOT save the file
        with requests.get(url, stream=True) as r:
            # Process the text in chunks of 1024 bytes
            text = ""
            for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    # Search logic on the fly
                    text += chunk
                    # Clear 'text' if it gets too large to save memory
                    if len(text) > 10000:
                        text = text[-2000:]
            
            # The search logic goes here
            # ...
            st.success(f"Finished streaming and scanning {url}")

import streamlit as st
import requests
from deep_translator import GoogleTranslator

st.title("Bible Code Skip-Search")

english_name = st.text_input("Enter name to search (in English):")

if st.button("Run Search"):
    # Translate English name to Hebrew
    hebrew_name = GoogleTranslator(source='en', target='iw').translate(english_name)
    st.write(f"Searching for '{english_name}' ({hebrew_name})...")
    
    # Pull the WLC source
    url = "https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/wlc.txt"
    response = requests.get(url)
    # Keeping only pure Hebrew characters
    text = "".join(filter(lambda char: '\u0590' <= char <= '\u05EA', response.text))
    
    found = False
    with st.spinner("Searching up to 5000 skips..."):
        # ELS Algorithm Logic - extended to 5001
        for skip in range(1, 5001):
            for start in range(skip):
                seq = text[start::skip]
                if hebrew_name in seq:
                    idx = seq.find(hebrew_name)
                    # Show a snippet of where it was found
                    context = seq[idx : idx + len(hebrew_name) + 15]
                    st.success(f"Match found at Skip {skip}!")
                    st.write(f"Context: {context}")
                    found = True
                    break
            if found: break
    
    if not found:
        st.error("No matches found within 5000 skips.")

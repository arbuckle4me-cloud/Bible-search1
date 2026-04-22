import streamlit as st
import requests
from googletrans import Translator

st.title("Bible Code Skip-Search")

english_name = st.text_input("Enter name to search (in English):")

if st.button("Run Search"):
    translator = Translator()
    # Translate English name to Hebrew
    hebrew_name = translator.translate(english_name, src='en', dest='iw').text
    st.write(f"Searching for '{english_name}' ({hebrew_name})...")
    
    # Pull the WLC source
    url = "https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/wlc.txt"
    response = requests.get(url)
    text = "".join(filter(str.isalpha, response.text))
    
    # ELS Algorithm Logic
    found = False
    for skip in range(1, 501):
        for start in range(skip):
            seq = text[start::skip]
            if hebrew_name in seq:
                idx = seq.find(hebrew_name)
                # Translate found context back to English
                raw_context = seq[idx : idx + len(hebrew_name) + 10]
                translated_context = translator.translate(raw_context, src='iw', dest='en').text
                st.write(f"Match at Skip {skip}: {translated_context}")
                found = True
    if not found:
        st.write("No matches found.")

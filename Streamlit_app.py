import streamlit as st
import requests
from deep_translator import GoogleTranslator

st.title("ELS Skip-Search Engine")

user_input = st.text_input("Enter term to search (English or Hebrew):")
max_skip = st.number_input("Maximum skip distance:", min_value=1, value=5000)

if st.button("Run Search"):
    # Determine if input is Hebrew, if not, translate
    if any('\u05D0' <= c <= '\u05EA' for c in user_input):
        search_term = user_input
    else:
        search_term = GoogleTranslator(source='en', target='iw').translate(user_input)
    
    st.write(f"Searching for sequence: **{search_term}**")
    
    # Pull the WLC source
    url = "https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/wlc.txt"
    response = requests.get(url)
    
    # Scrub text: only Hebrew consonants (א-ת)
    # This removes vowel points and cantillation marks
    raw_text = response.text
    text = "".join([c for c in raw_text if '\u05D0' <= c <= '\u05EA'])
    
    found = False
    
    # ELS Algorithm: Check every skip distance up to max_skip
    with st.spinner(f"Scanning up to {max_skip} skips..."):
        for skip in range(1, int(max_skip) + 1):
            # We check every possible starting point for this skip
            for start in range(skip):
                # Extract sequence based on skip interval
                seq = text[start::skip]
                
                if search_term in seq:
                    # Found it
                    idx = seq.find(search_term)
                    # Get surrounding context to verify
                    snippet = seq[idx : idx + len(search_term)]
                    
                    st.success(f"Match found at Skip Distance: **{skip}**")
                    st.write(f"Sequence identified: {snippet}")
                    found = True
                    break
            if found: break
    
    if not found:
        st.error(f"No matches found for '{search_term}' within {max_skip} skips.")

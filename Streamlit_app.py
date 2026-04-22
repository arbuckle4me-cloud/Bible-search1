import streamlit as st
import requests

st.title("Bible Code Skip-Search")

name = st.text_input("Enter name to search (Hebrew characters):")
if st.button("Run Search"):
    # Pull the WLC source
    url = "https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/wlc.txt"
    response = requests.get(url)
    text = "".join(filter(str.isalpha, response.text))
    
    st.write(f"Scanning for: {name}...")
    
    # ELS Algorithm Logic
    found = False
    for skip in range(1, 501):
        for start in range(skip):
            seq = text[start::skip]
            if name in seq:
                idx = seq.find(name)
                context = seq[idx : idx + len(name) + 15]
                st.write(f"Match found at Skip {skip}: {context}")
                found = True
    if not found:
        st.write("No matches found in this range.")

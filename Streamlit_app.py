import streamlit as st
import requests
import re
import time

st.title("EOTC Stride-Pattern Hunter")

# URLs
bible_canon = {
    "Genesis": "https://www.gutenberg.org/files/10/10-h/10-h.htm",
    "Enoch": "https://www.ccel.org/c/charles/otpseudepig/enoch/ENOCH_1.HTM",
    "Jubilees": "https://www.pseudepigrapha.com/jubilees/index.htm"
}

target = st.text_input("Enter pattern (e.g., CURT):").upper()
max_stride = st.number_input("Max skip distance:", min_value=1, max_value=500, value=100)

def get_clean_text(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        # Strip everything that isn't a letter
        return re.sub(r'[^a-zA-Z]', '', r.text.upper())
    except:
        return ""

if st.button("Run Stride Scan"):
    for book, url in bible_canon.items():
        st.write(f"--- Scanning {book} ---")
        text = get_clean_text(url)
        
        if not text:
            st.warning("Could not fetch.")
            continue
            
        found_any = False
        # The Stride Loop: 1 to max_stride
        for stride in range(1, max_stride + 1):
            # Check for the pattern at this specific stride
            # Pattern: Letter1, skip (stride-1), Letter2, skip (stride-1)...
            pattern = ""
            for i in range(len(target)):
                pattern += target[i] + ('.' * (stride - 1))
            
            # Use regex to find if this skip-sequence exists
            # We look for the sequence anywhere in the clean text
            if re.search(pattern, text):
                st.success(f"MATCH FOUND in {book} at skip-stride of {stride}!")
                found_any = True
                
        if not found_any:
            st.write("No matches found for this range.")
        time.sleep(0.5)

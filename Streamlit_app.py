import streamlit as st
import requests
import re
import time

st.title("EOTC Stride-Chain Extractor")

# URLs
bible_canon = {
    "Genesis": "https://www.gutenberg.org/files/10/10-h/10-h.htm",
    "Enoch": "https://www.ccel.org/c/charles/otpseudepig/enoch/ENOCH_1.HTM",
    "Jubilees": "https://www.pseudepigrapha.com/jubilees/index.htm"
}

target = st.text_input("Enter target pattern (e.g., HITLER):").upper()
max_stride = st.number_input("Max stride depth:", min_value=1, max_value=500, value=50)

def get_clean_text(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        # Convert to upper and remove everything except A-Z
        return re.sub(r'[^A-Z]', '', r.text.upper())
    except:
        return ""

if st.button("Run Extraction"):
    for book, url in bible_canon.items():
        st.subheader(f"--- Processing {book} ---")
        text = get_clean_text(url)
        
        if not text:
            st.warning("Could not reach site.")
            continue
            
        found_in_book = False
        
        # Iterate through strides
        for stride in range(1, max_stride + 1):
            # Create regex for the target pattern at current stride
            # Example stride 3: C..U..R..T
            pattern = ""
            for char in target:
                pattern += char + ('.' * (stride - 1))
            
            # Find all occurrences
            matches = re.finditer(pattern, text)
            
            for m in matches:
                found_in_book = True
                # Start index of the match
                start_pos = m.start()
                end_pos = m.end()
                
                # EXTRACT CHAIN: Continue from the end of the match
                # jumping by 'stride' until we get a chunk of text
                chain = ""
                current_idx = end_pos
                while current_idx < len(text) and len(chain) < 200:
                    chain += text[current_idx]
                    current_idx += stride
                
                st.success(f"Match found at stride {stride}!")
                st.write(f"**Pattern:** {target}")
                st.code(f"Chain following match: {chain}")
        
        if not found_in_book:
            st.write("No chains found for this stride range.")
        time.sleep(0.5)

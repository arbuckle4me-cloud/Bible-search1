import streamlit as st
import requests
import re

st.title("EOTC Global Direct-Link Hunter")

# Direct Cache Links (Fast & Reliable)
canon_links = {
    "KJV Bible": "https://www.gutenberg.org/cache/epub/10/pg10.txt",
    "Book of Mormon": "https://www.gutenberg.org/cache/epub/17/pg17.txt",
    "Quran": "https://www.gutenberg.org/cache/epub/16955/pg16955.txt",
    "Bhagavad Gita": "https://www.gutenberg.org/cache/epub/2388/pg2388.txt",
    "Tao Te Ching": "https://www.gutenberg.org/cache/epub/216/pg216.txt",
    "Dhammapada": "https://www.gutenberg.org/cache/epub/2017/pg2017.txt"
}

target = st.text_input("Enter pattern (e.g., HITLER):").upper()
max_stride = st.number_input("Max skip:", min_value=1, max_value=500, value=50)

if st.button("Start Global Raw Scan"):
    for name, url in canon_links.items():
        st.write(f"### Scanning {name}...")
        try:
            r = requests.get(url, timeout=10)
            text = re.sub(r'[^A-Z]', '', r.text.upper())
            
            for stride in range(1, max_stride + 1):
                pattern = "".join([c + ('.' * (stride - 1)) for c in target])
                matches = re.finditer(pattern, text)
                
                for m in matches:
                    chain = ""
                    curr = m.end()
                    while curr < len(text) and len(chain) < 200:
                        chain += text[curr]
                        curr += stride
                    
                    st.success(f"Match in {name} (Stride {stride})")
                    st.code(chain)
        except Exception as e:
            st.error(f"Could not load {name}: {e}")

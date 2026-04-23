# Replace your current loop inside the button with this:
if st.button("Execute Full Scan"):
    # ... (Crawler and Link setup remains the same)
    
    for i, link in enumerate(links):
        status = st.empty()
        status.text(f"Scanning: {link}...")
        try:
            text = requests.get(link, timeout=5).text.upper() # Added 5s timeout
            clean_text = re.sub(r'[^A-Z]', '', text)
            
            # Optimized Scan: Search for the first letter of your name first
            # to skip files where the name can't possibly exist
            first_char = name_to_search[0]
            for start in [m.start() for m in re.finditer(first_char, clean_text)]:
                for stride in range(min_stride, max_stride + 1):
                    # Check if the name fits in the remaining text
                    if start + (len(name_to_search) * stride) >= len(clean_text):
                        break
                    
                    # Verify the full sequence
                    match = True
                    for idx, char in enumerate(name_to_search):
                        if clean_text[start + (idx * stride)] != char:
                            match = False; break
                    if match:
                        st.success(f"MATCH FOUND! {name_to_search} at Stride {stride} in {link}")
                        # Display context
                        st.markdown(colorize(clean_text[start : start + (len(name_to_search)*stride)]))
        except Exception:
            continue 
        progress.progress((i + 1) / len(links))

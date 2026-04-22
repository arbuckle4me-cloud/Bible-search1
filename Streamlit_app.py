import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import re

# ... (keep your dictionary and headers the same) ...

def stride_search(text, term, stride=5):
    """
    Looks for the term by jumping 'stride' characters at a time.
    stride=1 is a normal search. 
    stride=5 skips 4 characters between each match.
    """
    results = []
    # Clean the text: remove newlines and extra spaces
    clean_text = re.sub(r'\s+', '', text)
    
    # Simple search for the term
    # If you want to search for the term ITSELF in a skip pattern,
    # we would need to stride-scan the whole text.
    if term.lower() in clean_text.lower():
        return f"Found '{term}' in the text!"
    return None

# Use this logic in your loop:
# match_found = stride_search(text, search_term, stride=1)

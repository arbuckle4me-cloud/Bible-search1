import requests
from bs4 import BeautifulSoup

# Define your library of online sources
# Replace these URLs with the direct text links for your chosen versions
bible_canon = {
    "Genesis": "https://example.com/genesis_text_link",
    "Exodus": "https://example.com/exodus_text_link",
    "Enoch": "https://example.com/enoch_text_link",
    # Add all 81 books here
}

def search_online_canon(search_term):
    for book_name, url in bible_canon.items():
        try:
            print(f"Searching {book_name}...")
            response = requests.get(url, timeout=10)
            
            # Clean the text
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text()
            
            # Perform the search
            if search_term in text:
                print(f"--- MATCH FOUND in {book_name} ---")
                # Add logic here to display or save the match
        
        except Exception as e:
            print(f"Could not access {book_name}: {e}")

# Execute
search_term = "Israel"
search_online_canon(search_term)

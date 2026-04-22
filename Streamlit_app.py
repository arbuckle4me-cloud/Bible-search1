import requests
from bs4 import BeautifulSoup
import time

# Library of verified online sources
# These links are structured for direct text access
bible_canon = {
    "Genesis (KJV)": "https://www.gutenberg.org/files/8001/8001-h/8001-h.htm",
    "Book of Enoch": "https://www.gutenberg.org/ebooks/77815.txt.utf-8",
    "Book of Jubilees": "https://sacred-texts.com/bib/jub/jub01.htm"
}

def search_online_canon(search_term):
    print(f"Starting search for: '{search_term}'")
    for book_name, url in bible_canon.items():
        try:
            print(f"Searching {book_name}...")
            response = requests.get(url, timeout=10)
            
            # Extract text
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text()
            
            # Simple containment check
            if search_term.lower() in text.lower():
                print(f"--- MATCH FOUND in {book_name} ---")
                return True # Stop at the first result
            
            time.sleep(1) # Be kind to the servers
            
        except Exception as e:
            print(f"Could not access {book_name}: {e}")
    
    print("No matches found.")
    return False

# Execute
if __name__ == "__main__":
    search_term = "Israel"
    search_online_canon(search_term)

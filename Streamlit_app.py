import requests
from bs4 import BeautifulSoup
import time

# Library of verified online sources
# These point to public domain or stable archive text versions
ethiopian_canon = {
    "Genesis (KJV)": "https://www.gutenberg.org/files/10/10-h/10-h.htm#chap01",
    "Book of Enoch": "https://www.gutenberg.org/ebooks/77815.txt.utf-8",
    "Book of Jubilees": "https://sacred-texts.com/bib/jub/jub01.htm",
    # Note: Meqabyan requires specific academic/archive links
    "Meqabyan_I": "https://archive.org/stream/TheFirstEthiopianBookOfMeqabyan/Meqabyan1_djvu.txt"
}

def search_online_canon(search_term):
    for book_name, url in ethiopian_canon.items():
        try:
            print(f"Searching {book_name}...")
            response = requests.get(url, timeout=15)
            
            # Simple cleaning for HTML or raw text
            if "gutenberg.org" in url or "sacred-texts.com" in url:
                soup = BeautifulSoup(response.content, "html.parser")
                text = soup.get_text()
            else:
                text = response.text
            
            if search_term in text:
                print(f"--- MATCH FOUND in {book_name} ---")
            
            # Throttle to be kind to the servers
            time.sleep(2)
            
        except Exception as e:
            print(f"Could not access {book_name}: {e}")

# Search Execution
if __name__ == "__main__":
    search_term = "Israel"
    search_online_canon(search_term)

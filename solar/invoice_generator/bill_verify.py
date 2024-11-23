import requests
from bs4 import BeautifulSoup

def verify_bill(reference_number):
    # List of URLs to try
    BILL_URLS = [
        "https://bill.pitc.com.pk/mepcobill/general",
        "https://bill.pitc.com.pk/mepcobill/industrial"
    ]
    
    for url in BILL_URLS:
        try:
            # Make the GET request
            response = requests.get(f"{url}?refno={reference_number}")
            
            # Parse the content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the "Bill Not Found!" marker
            bill_not_found = soup.find('h2')
            if bill_not_found and "Bill Not Found" in bill_not_found.text:
                print(f"Trying next URL: {url}")
                continue  # Try the next URL
            
            # If "Bill Not Found" is not present, assume the bill exists
            return {
                "exists": True,
                "message": "Bill found.",
                "source_url": url
            }
        
        except requests.exceptions.RequestException as e:
            # Handle network or request errors gracefully
            print(f"Error with URL {url}: {e}")
            continue
    
    # If no valid bill is found after trying all URLs
    return {"exists": False, "message": "Bill not found or invalid reference number."}

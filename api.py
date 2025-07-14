import requests
from config import API_KEY, API_URL

def lookup_barcode(barcode):
    params = {
        'barcode': barcode,
        'formatted': 'y',
        'key': API_KEY
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        products = response.json().get('products', [])
        if products:
            return products[0]  # First result
    return None

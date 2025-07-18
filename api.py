
import requests

# RapidAPI barcode lookup
RAPIDAPI_KEY = "564a5396d3msh94154227da876d1p173b65jsn193403cb56f0"
RAPIDAPI_HOST = "barcodes1.p.rapidapi.com"
RAPIDAPI_URL = "https://barcodes1.p.rapidapi.com/"

def lookup_barcode(barcode):
    url = RAPIDAPI_URL + "?query=" + str(barcode)
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            # ...existing code...
            product = result.get("product")
            if not product:
                products = result.get("products")
                if products and isinstance(products, list):
                    product = products[0]
            if not product:
                items = result.get("items")
                if items and isinstance(items, list):
                    product = items[0]
            if not product:
                if "title" in result or "description" in result:
                    product = result
            if product:
                # Build description: prefer 'description', else join 'features' if present
                description = product.get("description") or product.get("desc")
                if not description and product.get("features") and isinstance(product["features"], list):
                    description = "\n".join(product["features"])
                # Images: always return a list if present
                images = product.get("images")
                if not images:
                    images = product.get("image_urls")
                if not images and product.get("image"):
                    images = [product.get("image")]
                return {
                    "title": product.get("title") or product.get("name") or product.get("product_name"),
                    "description": description,
                    "images": images if images else None
                }
        return None
    except Exception as e:
        print(f"Barcode API error: {e}")
        return None

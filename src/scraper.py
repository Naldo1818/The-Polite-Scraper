from bs4 import BeautifulSoup
from datetime import datetime, timezone

def normalize_price(price_text):
    if not price_text:
        raise ValueError("Price is missing")

    cleaned = (
        price_text
        .replace("£", "")
        .replace("Â", "")
        .strip()
    )

    return float(cleaned)

def extract_book(html, product_url, source_page):
    soup = BeautifulSoup(html, "html.parser")

    product = soup.select_one("div.product_main")

    if product is None:
        raise ValueError("Product information not found")

    # Title
    title_element = product.select_one("h1")
    title = title_element.get_text(strip=True) if title_element else None

    # Price
    price_element = product.select_one(".price_color")
    price_text = price_element.get_text(strip=True) if price_element else None

    # Availability
    availability_element = product.select_one(".availability")
    availability_text = (
        availability_element.get_text(" ", strip=True)
        if availability_element
        else None
    )

    # Rating
    rating_element = product.select_one("p.star-rating")

    rating_text = None

    if rating_element:
        classes = rating_element.get("class", [])

        for rating in ["One", "Two", "Three", "Four", "Five"]:
            if rating in classes:
                rating_text = rating
                break

    # Description
    description_element = soup.select_one("#product_description + p")

    description = (
        description_element.get_text(strip=True)
        if description_element
        else None
    )

    # Timestamp
    fetched_at = datetime.now(timezone.utc).isoformat()

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }
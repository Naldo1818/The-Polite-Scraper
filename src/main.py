import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

BASE_URL = "https://books.toscrape.com/"
HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0"
}


def get_page(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    return response.text


def find_books(html, page_url):
    soup = BeautifulSoup(html, "html.parser")

    book_links = []

    for book in soup.select("article.product_pod h3 a"):
        href = book.get("href")

        if href:
            absolute_url = urljoin(page_url, href)
            book_links.append(absolute_url)

    return book_links


def find_next_page(html, page_url):
    soup = BeautifulSoup(html, "html.parser")

    next_link = soup.select_one("li.next a")

    if next_link:
        href = next_link.get("href")
        return urljoin(page_url, href)

    return None


def main():
    current_url = BASE_URL

    catalogue_pages = 0
    all_book_urls = []

    while catalogue_pages < 3 and current_url:
        print(f"Fetching catalogue page: {current_url}")

        html = get_page(current_url)

        catalogue_pages += 1

        books = find_books(html, current_url)
        all_book_urls.extend(books)

        print(f"Books found on this page: {len(books)}")

        time.sleep(0.5)

        current_url = find_next_page(html, current_url)

    unique_urls = list(dict.fromkeys(all_book_urls))

    print()
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_urls)}")


if __name__ == "__main__":
    main()
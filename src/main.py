import time
import requests

from scraper import extract_book


BASE_URL = "https://books.toscrape.com/"

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0"
}


def get_page(url):
    """
    Download a webpage and return its HTML.
    """

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    return response.text


def find_books(html, page_url):
    """
    Find all book links on a catalogue page.
    Convert relative URLs into absolute URLs.
    """

    from bs4 import BeautifulSoup
    from urllib.parse import urljoin

    soup = BeautifulSoup(html, "html.parser")

    book_links = []

    for book in soup.select("article.product_pod h3 a"):

        href = book.get("href")

        if href:
            absolute_url = urljoin(page_url, href)
            book_links.append(absolute_url)

    return book_links


def find_next_page(html, page_url):
    """
    Find the catalogue's next page link.
    """

    from bs4 import BeautifulSoup
    from urllib.parse import urljoin

    soup = BeautifulSoup(html, "html.parser")

    next_link = soup.select_one("li.next a")

    if next_link:
        href = next_link.get("href")

        if href:
            return urljoin(page_url, href)

    return None


def main():

    
    current_url = BASE_URL

    catalogue_pages = 0
    all_book_urls = []

    while catalogue_pages < 3 and current_url:

        print()
        print(f"Fetching catalogue page: {current_url}")

        try:

            html = get_page(current_url)

        except requests.RequestException as error:

            print(f"Failed to fetch catalogue page: {current_url}")
            print(f"Reason: {error}")

            break

        catalogue_pages += 1

        books = find_books(
            html,
            current_url
        )

        all_book_urls.extend(books)

        print(f"Books found on this page: {len(books)}")

        time.sleep(0.5)

        
        current_url = find_next_page(
            html,
            current_url
        )

    unique_urls = list(
        dict.fromkeys(all_book_urls)
    )

    print()
    print("--------------------------------")
    print("CATALOGUE DISCOVERY")
    print("--------------------------------")
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_urls)}")


    all_books = []

    print()
    print("--------------------------------")
    print("BOOK DETAIL EXTRACTION")
    print("--------------------------------")

    for index, book_url in enumerate(
        unique_urls,
        start=1
    ):

        print(
            f"Extracting book {index}/{len(unique_urls)}"
        )

        try:

            time.sleep(0.5)

            book_html = get_page(book_url)

            book = extract_book(
                book_html,
                book_url,
                BASE_URL
            )

            all_books.append(book)

        except requests.RequestException as error:

            print(
                f"Failed to fetch: {book_url}"
            )

            print(
                f"Reason: {error}"
            )

        except Exception as error:

            print(
                f"Failed to extract: {book_url}"
            )

            print(
                f"Reason: {error}"
            )


    print()
    print("--------------------------------")
    print("STAGE 3 CHECKPOINT")
    print("--------------------------------")

    print(
        f"detail_pages={len(all_books)}"
    )

    if all_books:

        print()
        print("Example raw record:")
        print()

        print(all_books[0])

    else:

        print("No books were extracted.")


if __name__ == "__main__":
    main()
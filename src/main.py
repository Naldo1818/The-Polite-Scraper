import time
import json
import os
import requests

from datetime import datetime, timezone

from scraper import extract_book, normalize_price
from models import Book


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


def get_page_with_retry(url):
    try:
        return get_page(url)

    except requests.Timeout:
        print("Request timed out. Retrying once...")
        time.sleep(1)

        return get_page(url)

    except requests.HTTPError as error:
        status_code = None

        if error.response is not None:
            status_code = error.response.status_code

        if status_code is not None and status_code >= 500:
            print(
                f"Server error {status_code}. Retrying once..."
            )

            time.sleep(1)

            return get_page(url)

        raise
def find_books(html, page_url):
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

    start_time = time.time()

    current_url = BASE_URL

    catalogue_pages = 0
    all_book_urls = []

    pages_fetched = 0
    failed_pages = 0

    all_books = []
    errors = []

    while catalogue_pages < 3 and current_url:

        print()
        print(f"Fetching catalogue page: {current_url}")

        try:

            time.sleep(0.5)

            html = get_page_with_retry(
                current_url
            )

            pages_fetched += 1

        except Exception as error:

            print(
                f"Failed to fetch catalogue page: {current_url}"
            )

            print(
                f"Reason: {error}"
            )

            failed_pages += 1

            break

        catalogue_pages += 1

        books = find_books(
            html,
            current_url
        )

        all_book_urls.extend(books)

        print(
            f"Books found on this page: {len(books)}"
        )

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
    print(
        f"catalogue_pages={catalogue_pages}"
    )
    print(
        f"discovered={len(all_book_urls)}"
    )
    print(
        f"unique_urls={len(unique_urls)}"
    )

    print()
    print("--------------------------------")
    print("BOOK DETAIL EXTRACTION")
    print("--------------------------------")

    for index, book_url in enumerate(
        unique_urls,
        start=1
    ):

        print(
            f"Processing book {index}/{len(unique_urls)}"
        )

        try:

            time.sleep(0.5)

            book_html = get_page_with_retry(
                book_url
            )

            pages_fetched += 1

            book = extract_book(
                book_html,
                book_url,
                BASE_URL
            )

            book["price_gbp"] = normalize_price(
                book["price_text"]
            )

            validated_book = Book(**book)

            all_books.append(
                validated_book.model_dump(
                    mode="json"
                )
            )

        except requests.HTTPError as error:

            status_code = None

            if error.response is not None:
                status_code = error.response.status_code

            print(
                f"Failed to process: {book_url}"
            )

            print(
                f"HTTP status: {status_code}"
            )

            failed_pages += 1

            errors.append({
                "product_url": book_url,
                "reason": str(error),
                "status_code": status_code
            })

        except Exception as error:

            print(
                f"Failed to process: {book_url}"
            )

            print(
                f"Reason: {error}"
            )

            failed_pages += 1

            errors.append({
                "product_url": book_url,
                "reason": str(error)
            })

    os.makedirs(
        "output",
        exist_ok=True
    )

    with open(
        "output/books.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_books,
            file,
            indent=2,
            ensure_ascii=False
        )

    with open(
        "output/errors.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            errors,
            file,
            indent=2,
            ensure_ascii=False
        )

    duration = round(
        time.time() - start_time,
        2
    )

    run_report = {
        "started_at": datetime.fromtimestamp(
            start_time,
            timezone.utc
        ).isoformat(),

        "duration_seconds": duration,

        "catalogue_pages": catalogue_pages,

        "pages_fetched": pages_fetched,

        "failed_pages": failed_pages,

        "discovered": len(all_book_urls),

        "unique_urls": len(unique_urls),

        "valid_records": len(all_books),

        "invalid_records": len(errors)
    }

    with open(
        "output/run-report.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            run_report,
            file,
            indent=2
        )

    print()
    print("--------------------------------")
    print("STAGE 5 CHECKPOINT")
    print("--------------------------------")

    print(
        f"valid_records={len(all_books)}"
    )

    print(
        f"invalid_records={len(errors)}"
    )

    print(
        f"failed_pages={failed_pages}"
    )

    print(
        f"pages_fetched={pages_fetched}"
    )

    print(
        f"duration_seconds={duration}"
    )

    print(
        "run-report.json saved to output/run-report.json"
    )


if __name__ == "__main__":
    main()
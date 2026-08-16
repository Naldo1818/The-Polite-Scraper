# The Polite Scraper

A small Python scraper that collects book data from Books to Scrape and converts the scraped HTML into validated JSON.

## What it does

The scraper:

- Checks the target website before collecting data
- Uses a descriptive User-Agent
- Waits at least 0.5 seconds between real requests
- Discovers three catalogue pages using the site's Next link
- Discovers 60 unique book URLs
- Extracts book details from each product page
- Normalizes prices such as `£51.77` into numeric GBP values
- Validates records using Pydantic
- Stores valid records in `output/books.json`
- Stores invalid records in `output/errors.json`
- Produces a run report in `output/run-report.json`
- Handles failed pages without crashing
- Retries timeouts and server errors once
- Does not retry 403 or 404 responses

## Project Structure

```text
src/
├── main.py
├── scraper.py
└── models.py

output/
├── books.json
├── errors.json
└── run-report.json
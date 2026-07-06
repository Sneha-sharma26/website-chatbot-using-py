"""
1. Connects to the target website using `requests`
2. Parses the HTML using `BeautifulSoup`
3. Extracts the visible text
4. Saves it into a local file called website_content.txt
"""

import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


URL = "https://phoenixdigitaltech.net/"
OUTPUT_FILE = "website_content.txt"


MAX_PAGES = 20
DELAY_BETWEEN_REQUESTS = 1.0

# Some websites block requests that don't look like they come from a real browser.
# User-Agent header helps 
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def fetch_page(url: str) -> str:
    """Download the raw HTML of a page."""
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()  # throws an error if the request failed
    return response.text

def extract_text(html: str) -> str:
    """
    Turn raw HTML into clean, readable text.
    We remove script/style tags because they contain code, not content.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove tags that don't contain useful readable text
    for tag in soup(["script", "style", "noscript", "svg", "footer", "header",  "nav", "aside", "form", "button"]):
        tag.decompose()

    # get_text() pulls out all visible text; separator adds spacing
    raw_text = soup.get_text(separator="\n")

    # Clean up: remove empty lines and extra whitespace
    lines = [line.strip() for line in raw_text.splitlines()]
    lines = [line for line in lines if line]  # drop empty lines
    
    NAV_LABELS = {
        "home", "who we are", "about", "about us", "contact",
        "contact us", "services", "careers", "blog", "login",
        "sign up", "get started", "menu", "search", "privacy policy",
        "terms of service", "terms & conditions", "read more",
        "learn more", "our partners",
    }
    lines = [line for line in lines if line.lower() not in NAV_LABELS]
    
    clean_text = "\n".join(lines)

    return clean_text

def save_to_file(text: str, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved {len(text)} characters to {filename}")


# Multi-page crawling helpers
def normalize_url(url: str) -> str:
    # Strip query strings/#fragments and trailing slash to avoid duplicates
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def get_internal_links(html: str, base_url: str) -> list[str]:
    # Find links on this page that point to the same website.
    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(base_url).netloc

    skip_extensions = (
        ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
        ".zip", ".doc", ".docx", ".xls", ".xlsx", ".mp4", ".mp3",
        ".css", ".js",
    )

    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue

        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        if parsed.netloc != base_domain:
            continue
        if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
            continue

        links.append(normalize_url(full_url))

    return links


def main():
    print(f"Starting crawl at {URL} (limit: {MAX_PAGES} pages)")

    to_visit = [normalize_url(URL)]
    visited = set()
    all_text_parts = []

    while to_visit and len(visited) < MAX_PAGES:
        page_url = to_visit.pop(0)
        if page_url in visited:
            continue
        visited.add(page_url)

        print(f"  Fetching ({len(visited)}/{MAX_PAGES}): {page_url}")
        try:
            html = fetch_page(page_url)
        except requests.exceptions.RequestException as e:
            print(f"Skipped (couldn't fetch): {e}")
            continue

        text = extract_text(html)
        if text:
            all_text_parts.append(text)

        # Queue up any new internal links found on this page
        for link in get_internal_links(html, page_url):
            if link not in visited and link not in to_visit:
                to_visit.append(link)

        time.sleep(DELAY_BETWEEN_REQUESTS)  # be polite to the server

    print(f"Crawled {len(visited)} page(s) total.")

    combined_text = "\n".join(all_text_parts)

    if not combined_text:
        print("No text was extracted.")
        return

    save_to_file(combined_text, OUTPUT_FILE)


if __name__ == "__main__":
    main()
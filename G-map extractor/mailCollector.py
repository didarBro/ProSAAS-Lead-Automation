import csv
import re
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm  # for progress bar

# ================= CONFIG =================
INPUT_FILE = "Real_estate_companies_220_records.csv"
OUTPUT_FILE = "Real_estate_companies_mail.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_SITE_TIME = 300          # Max 5 minutes per website
EXTRA_PAGES_LIMIT = 3        # Limit contact/about pages to 3
DEFAULT_REQUEST_TIMEOUT = (3, 3)  # per-request timeout
MAX_RETRIES = 3              # Maximum retries per page
# ==========================================

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

SOCIAL_DOMAINS = {
    "Facebook Links": "facebook.com",
    "Linkedin Links": "linkedin.com",
    "Instagram Links": "instagram.com",
    "Twitter Links": "twitter.com",
    "Youtube Links": "youtube.com",
    "Tiktok Links": "tiktok.com",
}


def fetch_html(url, remaining_time):
    """Fetch URL HTML with timeout."""
    if remaining_time <= 0:
        return None
    try:
        connect_timeout = min(DEFAULT_REQUEST_TIMEOUT[0], remaining_time)
        read_timeout = min(DEFAULT_REQUEST_TIMEOUT[1], remaining_time)
        res = requests.get(url, headers=HEADERS, timeout=(connect_timeout, read_timeout))
        if res.status_code == 200:
            return res.text
    except Exception:
        pass
    return None


def fetch_with_retries(url, remaining_time):
    """Try fetching a URL up to MAX_RETRIES times."""
    for attempt in range(1, MAX_RETRIES + 1):
        html = fetch_html(url, remaining_time)
        if html:
            return html
        print(f"⚠️ Attempt {attempt} failed for {url}")
    return None


def extract_emails(html):
    return set(EMAIL_REGEX.findall(html))


def extract_social_links(soup):
    socials = {k: set() for k in SOCIAL_DOMAINS}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        for name, domain in SOCIAL_DOMAINS.items():
            if domain in href:
                socials[name].add(href)
    return socials


def find_extra_pages(soup, base_url):
    pages = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if any(x in href for x in ["contact", "about"]):
            pages.add(urljoin(base_url, a["href"]))
    return pages


# ================= MAIN PROCESS =================
total_sites = 0
success_sites = 0
total_emails = 0

with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:

    reader = list(csv.DictReader(infile))
    fieldnames = reader[0].keys()
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for idx, row in enumerate(reader, start=1):
        website = row.get("Website", "").strip()
        if not website:
            writer.writerow(row)
            continue

        total_sites += 1
        start_time = time.time()
        print(f"\n🔍 Crawling ({total_sites}): {website}")

        if not website.startswith("http"):
            website = "https://" + website

        # Extract homepage from CSV URL
        parsed = urlparse(website)
        homepage = f"{parsed.scheme}://{parsed.netloc}"

        emails = set()
        socials = {k: set() for k in SOCIAL_DOMAINS}

        # ------------------ Crawl homepage ------------------
        remaining_time = MAX_SITE_TIME - (time.time() - start_time)
        html_home = fetch_with_retries(homepage, remaining_time)
        if html_home:
            emails.update(extract_emails(html_home))
            soup_home = BeautifulSoup(html_home, "html.parser")
            homepage_socials = extract_social_links(soup_home)
            for key in SOCIAL_DOMAINS:
                socials[key].update(homepage_socials[key])
        else:
            print(f"❌ Failed to load homepage after {MAX_RETRIES} attempts")
            writer.writerow(row)
            continue  # Skip to next website

        # ------------------ Crawl CSV page ------------------
        remaining_time = MAX_SITE_TIME - (time.time() - start_time)
        html_page = fetch_with_retries(website, remaining_time)
        if html_page:
            emails.update(extract_emails(html_page))
            soup_page = BeautifulSoup(html_page, "html.parser")
            page_socials = extract_social_links(soup_page)
            for key in SOCIAL_DOMAINS:
                socials[key].update(page_socials[key])
        else:
            print(f"❌ Failed to load CSV page after {MAX_RETRIES} attempts")

        # ------------------ Crawl extra pages (contact/about) ------------------
        combined_soup = soup_home if html_home else (soup_page if html_page else None)
        if combined_soup:
            extra_pages = list(find_extra_pages(combined_soup, homepage))[:EXTRA_PAGES_LIMIT]
            for page_idx, page in enumerate(extra_pages, start=1):
                remaining_time = MAX_SITE_TIME - (time.time() - start_time)
                if remaining_time <= 0:
                    print("⏭ Skipped remaining pages (exceeded 5 min)")
                    break

                page_html = fetch_with_retries(page, remaining_time)
                if page_html:
                    emails.update(extract_emails(page_html))

                # Progress bar for extra pages
                print(f"Pages: {int(page_idx/len(extra_pages)*100)}%|{'█'*int(page_idx/len(extra_pages)*50)}{' '*(50-int(page_idx/len(extra_pages)*50))} {page_idx}/{len(extra_pages)}", end='\r')

        # ------------------ Update row ------------------
        row["Emails"] = ", ".join(sorted(emails))
        for key in SOCIAL_DOMAINS:
            row[key] = ", ".join(sorted(socials[key]))

        if emails or any(socials.values()):
            success_sites += 1
            total_emails += len(emails)

        writer.writerow(row)
        print(f"\n✅ Emails: {len(emails)} | Social Links: {sum(len(s) for s in socials.values())}")

# ================= SUMMARY =================
print("\n========== CRAWLING SUMMARY ==========")
print(f"Total Websites Processed : {total_sites}")
print(f"Successful Extractions   : {success_sites}")
print(f"Total Emails Found       : {total_emails}")
print(f"Output File              : {OUTPUT_FILE}")
print("=====================================")

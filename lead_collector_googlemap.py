"""
USA Lead Collector – Safe Incremental Version
- No cities, USA only
- 3 pages deep
- Timer limit
- Incremental saving
- Progress + Summary
"""

import requests
import csv
import os
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime

# ================= CONFIG =================
API_KEY = "AIzaSyB12rbOOzlLLCC_gWR3K0zBYVIal7R-7FI"
OUTPUT_FILE = "usa_leads.csv"

SEARCH_QUERIES = [
    "marketing agency",
    "software company",
    "IT services company",
    "digital marketing",
    "web development",
    "SEO agency",
    "cloud services",
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

MAX_PAGES = 3          # Deep only 3 pages
GLOBAL_TIME_LIMIT = 8 * 60   # 8 minutes (free limit safety)
REQUEST_DELAY = 1.2

# ================= FILE INIT =================
def init_output_file():
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Company Name",
                "Website",
                "Email",
                "Phone",
                "Address",
                "Social Links",
                "Category",
                "Source",
                "Date Added"
            ])
        print(f"📁 Output file created: {OUTPUT_FILE}")

def append_row(row):
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

# ================= SCRAPERS =================
def extract_emails(text):
    return re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)

def extract_social_links(html):
    socials = set()
    for a in html.find_all("a", href=True):
        link = a["href"]
        if any(x in link for x in ["facebook.com", "linkedin.com", "twitter.com", "instagram.com"]):
            socials.add(link)
    return ", ".join(list(socials)[:5])

def get_email_and_socials(url):
    if not url:
        return "", ""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text()
        emails = extract_emails(text)
        socials = extract_social_links(soup)
        return (emails[0] if emails else "", socials)
    except:
        return "", ""

# ================= GOOGLE API =================
def search_places(query, next_page_token=None):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{query} in USA",
        "key": API_KEY,
        "region": "us",
        "type": "establishment",
    }
    if next_page_token:
        params["pagetoken"] = next_page_token

    r = requests.get(url, params=params).json()
    return r

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,website,formatted_address,formatted_phone_number",
        "key": API_KEY,
    }
    r = requests.get(url, params=params).json()
    return r.get("result", {})

# ================= MAIN =================
def collect_leads():
    start_time = time.time()
    total_collected = 0
    total_queries = len(SEARCH_QUERIES)

    init_output_file()

    for qi, search_key in enumerate(SEARCH_QUERIES, start=1):

        if time.time() - start_time > GLOBAL_TIME_LIMIT:
            print("⏰ Global time limit reached. Stopping safely.")
            break

        print(f"\n🔍 [{qi}/{total_queries}] Searching: {search_key} (USA)")

        next_token = None
        page = 0

        while page < MAX_PAGES:
            if time.time() - start_time > GLOBAL_TIME_LIMIT:
                print("⏰ Time limit reached mid-search.")
                break

            data = search_places(search_key, next_token)

            results = data.get("results", [])
            next_token = data.get("next_page_token")

            if not results:
                break

            page += 1
            print(f"   📄 Page {page} | Results: {len(results)}")

            for idx, place in enumerate(results, start=1):

                if time.time() - start_time > GLOBAL_TIME_LIMIT:
                    break

                details = get_place_details(place["place_id"])

                name = details.get("name", "")
                website = details.get("website", "")
                address = details.get("formatted_address", "")
                phone = details.get("formatted_phone_number", "")

                email, socials = get_email_and_socials(website)

                row = [
                    name,
                    website,
                    email,
                    phone,
                    address,
                    socials,
                    search_key,     # Category from search keyword
                    "Google Maps",
                    datetime.now().strftime("%Y-%m-%d"),
                ]

                append_row(row)
                total_collected += 1

                print(f"      ✅ {total_collected}. {name} | {email}")

                time.sleep(REQUEST_DELAY)

            if next_token:
                print("   ⏳ Waiting for next page token...")
                time.sleep(2)
            else:
                break

    # ================= SUMMARY =================
    print("\n🎉 COLLECTION FINISHED")
    print(f"Total Leads Collected: {total_collected}")
    print(f"Output File: {OUTPUT_FILE}")
    print(f"Time Spent: {round(time.time() - start_time, 1)} sec")


if __name__ == "__main__":
    collect_leads()

import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time
from urllib.parse import urljoin, urlparse

# ================= CONFIG =================
API_KEY = "AIzaSyB12rbOOzlLLCC_gWR3K0zBYVIal7R-7FI"
CX = "85b02be9bcb384e72"

OUTPUT_FILE = r"D:\Prosaas Lead collector\LeadsFromGoogle\us_leads_google_2.csv"

HEADERS = {"User-Agent": "Mozilla/5.0"}

MAX_RUNTIME_SECONDS = 7200
MAX_SITE_TIME = 300
EXTRA_PAGES_LIMIT = 5
REQUEST_TIMEOUT = (5, 5)
MAX_RETRIES = 3

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

SOCIAL_DOMAINS = {
    "Facebook": "facebook.com",
    "LinkedIn": "linkedin.com",
    "Instagram": "instagram.com",
    "Twitter": "twitter.com",
    "YouTube": "youtube.com",
    "TikTok": "tiktok.com",
}

SEARCH_KEYS = [
    "HVAC & AC repair",
    "Electricians",
    "Plumbing services",
    "Roofing contractors",
    "Pest control",
    "Locksmiths",
    "Cleaning services",
    "Auto repair shops",
    "Auto body shops",
    "Tire shops",
    "Dental clinics",
    "Orthodontists",
    "Chiropractors",
    "Physical therapy clinics",
    "Veterinary clinics",
    "Real estate agents",
    "Property management companies",
    "Home inspection services",
    "Handyman services",
    "General contractors",
    "Remodeling contractors",
    "Kitchen & bath remodelers",
    "Flooring contractors",
    "Carpet installation services",
    "Window & door installation",
    "Garage door repair",
    "Landscaping services",
    "Lawn care companies",
    "Tree removal services",
    "Pool cleaning services",
    "Pool installation companies",
    "Pressure washing services",
    "Water damage restoration",
    "Mold remediation services",
    "Fire damage restoration",
    "Moving companies",
    "Junk removal services",
    "Storage facilities",
    "Security system installers",
    "Home automation services",
    "Solar panel installers",
    "Insulation contractors",
    "Fence installation companies",
    "Concrete contractors",
    "Asphalt & paving contractors",
    "Painting contractors",
    "Drywall repair services",
    "Interior designers",
    "Architectural firms",
    "Engineering firms",
    "IT support services",
    "Managed IT services",
    "Digital marketing agencies",
    "SEO agencies",
    "Web design agencies",   
    "Advertising agencies",
    "Branding agencies",
    "PR agencies",
    "Accounting firms",
    "Bookkeeping services",
    "Tax preparation services",
    "Financial advisors",
    "Insurance agencies",
    "Law firms",
    "Personal injury lawyers",
    "Family law attorneys",
    "Immigration law firms",
    "Estate planning attorneys",
    "Mortgage brokers",
    "Loan officers",
    "Title companies",
    "Notary services",
    "Business consulting firms"
]


START_TIME = time.time()

# ================= FILE INIT =================
def init_file():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    if not os.path.exists(OUTPUT_FILE):
        df = pd.DataFrame(columns=[
            "Company Name", "Website", "Emails",
            "Facebook", "LinkedIn", "Instagram",
            "Twitter", "YouTube", "TikTok",
            "Category", "Date Added"
        ])
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"📄 Output file created: {OUTPUT_FILE}")

def save_row(row):
    pd.DataFrame([row]).to_csv(
        OUTPUT_FILE,
        mode="a",
        header=False,
        index=False
    )

# ================= GOOGLE SEARCH =================
def google_search(query, start):
    print(f"\n🔍 Google Search: {query} | start={start}")
    try:
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params = {
                "key": API_KEY,
                "cx": CX,
                "q": query,
                "num": 10,
                "start": start,
                "gl": "us",      # geolocation
                "hl": "en",      # language
            },
            timeout=10
        )
        r.raise_for_status()
        return r.json().get("items", [])
    except Exception as e:
        print("❌ Google API error:", e)
        return []

# ================= REQUEST HELPERS =================
def fetch_with_retries(url, remaining_time):
    for attempt in range(1, MAX_RETRIES + 1):
        if remaining_time <= 0:
            return None
        try:
            r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                print(f"   ✅ Loaded ({attempt}): {url}")
                return r.text
        except Exception:
            pass
        print(f"   🔁 Retry {attempt}/{MAX_RETRIES}: {url}")
    print(f"   ❌ Failed: {url}")
    return None

# ================= EXTRACTION =================
def extract_emails(html):
    return set(EMAIL_REGEX.findall(html))

def extract_socials(soup):
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
        if any(x in href for x in ["contact", "about", "support", "company"]):
            pages.add(urljoin(base_url, a["href"]))
    return list(pages)[:EXTRA_PAGES_LIMIT]

# ================= MAIN =================
print("\n🚀 GOOGLE SEARCH + WEBSITE CRAWLING STARTED\n")
init_file()

total_sites = 0
sites_with_email = 0
total_emails = 0

for key in SEARCH_KEYS:
    if time.time() - START_TIME > MAX_RUNTIME_SECONDS:
        break

    print(f"\n========== CATEGORY: {key} ==========")
    query = f"{key} company USA"

    for start in range(1, 100, 10):
        results = google_search(query, start)
        if not results:
            break

        for item in results:
            if time.time() - START_TIME > MAX_RUNTIME_SECONDS:
                break

            name = item.get("title", "").split("|")[0].strip()
            website = item.get("link", "")
            if not website:
                continue

            total_sites += 1
            print(f"\n🌐 ({total_sites}) Crawling: {website}")

            emails = set()
            socials = {k: set() for k in SOCIAL_DOMAINS}
            site_start = time.time()

            if not website.startswith("http"):
                website = "https://" + website

            parsed = urlparse(website)
            homepage = f"{parsed.scheme}://{parsed.netloc}"

            # Homepage
            html_home = fetch_with_retries(homepage, MAX_SITE_TIME)
            soup_home = None
            if html_home:
                found = extract_emails(html_home)
                emails.update(found)
                print(f"   ✉️ Homepage emails: {len(found)}")
                soup_home = BeautifulSoup(html_home, "html.parser")
                home_socials = extract_socials(soup_home)
                for k in SOCIAL_DOMAINS:
                    socials[k].update(home_socials[k])

            # Extra pages
            if soup_home and not emails:
                pages = find_extra_pages(soup_home, homepage)
                print(f"   📂 Extra pages: {len(pages)}")
                for p in pages:
                    remaining = MAX_SITE_TIME - (time.time() - site_start)
                    html_p = fetch_with_retries(p, remaining)
                    if html_p:
                        found = extract_emails(html_p)
                        emails.update(found)
                        print(f"      ✉️ Emails found: {len(found)}")
                        if found:
                            break

            if emails:
                sites_with_email += 1
                total_emails += len(emails)

            row = {
                "Company Name": name,
                "Website": website,
                "Emails": ", ".join(sorted(emails)),
                "Category": key,
                "Date Added": datetime.now().strftime("%Y-%m-%d")
            }

            for k in SOCIAL_DOMAINS:
                row[k] = ", ".join(sorted(socials[k]))

            save_row(row)
            print(f"   ✅ Saved | Emails: {len(emails)}")
            time.sleep(1)

# ================= SUMMARY =================
elapsed = int(time.time() - START_TIME)

print("\n================ FINAL SUMMARY ================")
print(f"🌐 Total Websites Crawled : {total_sites}")
print(f"✉️ Websites with Emails  : {sites_with_email}")
print(f"📧 Total Emails Found    : {total_emails}")
print(f"⏱ Time Taken (sec)       : {elapsed}")
print(f"📁 Output File           : {OUTPUT_FILE}")
print("==============================================")

# import csv
# import re
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse

# # ================= CONFIG =================
# INPUT_FILE = "IT_services_company_in_United_States_of_America_220_records.csv"
# OUTPUT_FILE = "IT_services_company_mail.csv"
# HEADERS = {"User-Agent": "Mozilla/5.0"}
# TIMEOUT = 10
# # ==========================================

# EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# SOCIAL_DOMAINS = {
#     "facebook": "facebook.com",
#     "linkedin": "linkedin.com",
#     "instagram": "instagram.com",
#     "twitter": "twitter.com",
#     "youtube": "youtube.com",
#     "tiktok": "tiktok.com"
# }


# def fetch_html(url):
#     try:
#         response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
#         if response.status_code == 200:
#             return response.text
#     except Exception:
#         pass
#     return None


# def extract_emails(html):
#     return set(EMAIL_REGEX.findall(html))


# def extract_social_links(soup):
#     socials = {key: set() for key in SOCIAL_DOMAINS}

#     for link in soup.find_all("a", href=True):
#         href = link["href"]
#         for name, domain in SOCIAL_DOMAINS.items():
#             if domain in href:
#                 socials[name].add(href)

#     return socials


# def find_extra_pages(soup, base_url):
#     pages = set()
#     for link in soup.find_all("a", href=True):
#         href = link["href"].lower()
#         if any(x in href for x in ["contact", "about"]):
#             pages.add(urljoin(base_url, link["href"]))
#     return pages


# # ================= MAIN PROCESS =================
# total_sites = 0
# success_sites = 0
# total_emails = 0

# with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
#      open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:

#     reader = csv.DictReader(infile)
#     fieldnames = [
#         "Website",
#         "Emails",
#         "Facebook",
#         "LinkedIn",
#         "Instagram",
#         "Twitter",
#         "YouTube",
#         "TikTok"
#     ]

#     writer = csv.DictWriter(outfile, fieldnames=fieldnames)
#     writer.writeheader()

#     for row in reader:
#         website = row.get("Website", "").strip()
#         if not website:
#             continue

#         total_sites += 1
#         print(f"\n🔍 Crawling ({total_sites}): {website}")

#         if not website.startswith("http"):
#             website = "https://" + website

#         html = fetch_html(website)
#         if not html:
#             print("❌ Failed to load website")
#             continue

#         soup = BeautifulSoup(html, "html.parser")

#         emails = extract_emails(html)
#         socials = extract_social_links(soup)

#         # Crawl contact/about pages
#         extra_pages = find_extra_pages(soup, website)
#         for page in extra_pages:
#             page_html = fetch_html(page)
#             if page_html:
#                 emails.update(extract_emails(page_html))

#         if emails or any(socials.values()):
#             success_sites += 1
#             total_emails += len(emails)

#         writer.writerow({
#             "Website": website,
#             "Emails": ", ".join(emails),
#             "Facebook": ", ".join(socials["facebook"]),
#             "LinkedIn": ", ".join(socials["linkedin"]),
#             "Instagram": ", ".join(socials["instagram"]),
#             "Twitter": ", ".join(socials["twitter"]),
#             "YouTube": ", ".join(socials["youtube"]),
#             "TikTok": ", ".join(socials["tiktok"]),
#         })

#         print(f"✅ Emails: {len(emails)} | Socials found")

# # ================= SUMMARY =================
# print("\n========== CRAWLING SUMMARY ==========")
# print(f"Total Websites Processed : {total_sites}")
# print(f"Successful Extractions   : {success_sites}")
# print(f"Total Emails Found       : {total_emails}")
# print(f"Output File              : {OUTPUT_FILE}")
# print("=====================================")


import csv
import re
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ================= CONFIG =================
INPUT_FILE = "IT_services_company_in_United_States_of_America_220_records.csv"
OUTPUT_FILE = "IT_services_company_mail.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}
REQUEST_TIMEOUT = 10           # per request timeout (seconds)
MAX_SITE_TIME = 600            # 10 minutes per website
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


def fetch_html(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            return res.text
    except Exception:
        pass
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

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames  # keep ALL input columns

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        website = row.get("Website", "").strip()
        if not website:
            writer.writerow(row)
            continue

        total_sites += 1
        start_time = time.time()
        print(f"\n🔍 Crawling ({total_sites}): {website}")

        if not website.startswith("http"):
            website = "https://" + website

        html = fetch_html(website)
        if not html:
            print("❌ Failed to load website")
            writer.writerow(row)
            continue

        soup = BeautifulSoup(html, "html.parser")

        emails = extract_emails(html)
        socials = extract_social_links(soup)

        # Crawl contact/about pages
        extra_pages = find_extra_pages(soup, website)
        for page in extra_pages:
            # ⏱ Check 10-minute limit
            if time.time() - start_time > MAX_SITE_TIME:
                print("⏭ Skipped (exceeded 10-minute limit)")
                break

            page_html = fetch_html(page)
            if page_html:
                emails.update(extract_emails(page_html))

        # Update row values
        row["Emails"] = ", ".join(sorted(emails))
        for key in SOCIAL_DOMAINS:
            row[key] = ", ".join(sorted(socials[key]))

        if emails or any(socials.values()):
            success_sites += 1
            total_emails += len(emails)

        writer.writerow(row)
        print(f"✅ Emails: {len(emails)} | Socials found")

# ================= SUMMARY =================
print("\n========== CRAWLING SUMMARY ==========")
print(f"Total Websites Processed : {total_sites}")
print(f"Successful Extractions   : {success_sites}")
print(f"Total Emails Found       : {total_emails}")
print(f"Output File              : {OUTPUT_FILE}")
print("=====================================")

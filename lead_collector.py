# import requests
# import pandas as pd
# import re
# from bs4 import BeautifulSoup
# from datetime import datetime
# import os
# import time
# from requests.exceptions import RequestException

# # ================= CONFIG =================
# API_KEY = "AIzaSyB12rbOOzlLLCC_gWR3K0zBYVIal7R-7FI"
# CX = "85b02be9bcb384e72"

# OUTPUT_FILE = r"C:\Users\didar\Documents\Prosaas\Google_Search_Script\us_leads_google_2.csv"

# SEARCH_KEYS = [
#     "HVAC & AC repair",
#     "Electricians",
#     "Plumbing services",
#     "Roofing contractors",
#     "Pest control",
#     "Locksmiths",
#     "Cleaning services",
#     "Auto repair shops",
#     "Auto body shops",
#     "Tire shops",
#     "Dental clinics",
#     "Orthodontists",
#     "Chiropractors",
#     "Physical therapy clinics",
#     "Veterinary clinics",
#     "Real estate agents",
#     "Property management companies",
#     "Home inspection services",
#     "Handyman services",
#     "General contractors",
#     "Remodeling contractors",
#     "Kitchen & bath remodelers",
#     "Flooring contractors",
#     "Carpet installation services",
#     "Window & door installation",
#     "Garage door repair",
#     "Landscaping services",
#     "Lawn care companies",
#     "Tree removal services",
#     "Pool cleaning services",
#     "Pool installation companies",
#     "Pressure washing services",
#     "Water damage restoration",
#     "Mold remediation services",
#     "Fire damage restoration",
#     "Moving companies",
#     "Junk removal services",
#     "Storage facilities",
#     "Security system installers",
#     "Home automation services",
#     "Solar panel installers",
#     "Insulation contractors",
#     "Fence installation companies",
#     "Concrete contractors",
#     "Asphalt & paving contractors",
#     "Painting contractors",
#     "Drywall repair services",
#     "Interior designers",
#     "Architectural firms",
#     "Engineering firms",
#     "IT support services",
#     "Managed IT services",
#     "Digital marketing agencies",
#     "SEO agencies",
#     "Web design agencies",   
#     "Advertising agencies",
#     "Branding agencies",
#     "PR agencies",
#     "Accounting firms",
#     "Bookkeeping services",
#     "Tax preparation services",
#     "Financial advisors",
#     "Insurance agencies",
#     "Law firms",
#     "Personal injury lawyers",
#     "Family law attorneys",
#     "Immigration law firms",
#     "Estate planning attorneys",
#     "Mortgage brokers",
#     "Loan officers",
#     "Title companies",
#     "Notary services",
#     "Business consulting firms"
# ]

# HEADERS = {"User-Agent": "Mozilla/5.0"}

# MAX_RUNTIME_SECONDS = 7200     # 9 minutes safety
# START_TIME = time.time()

# # ================= FILE INIT =================
# def init_file():
#     output_dir = os.path.dirname(OUTPUT_FILE)
#     os.makedirs(output_dir, exist_ok=True)

#     if not os.path.exists(OUTPUT_FILE):
#         df = pd.DataFrame(columns=[
#             "Company Name",
#             "Website",
#             "Email",
#             "Address",
#             "Social Links",
#             "Category",
#             "Date Added"
#         ])
#         df.to_csv(OUTPUT_FILE, index=False)

# # ================= SAVE ONE ROW =================
# def append_row(row_dict):
#     try:
#         output_dir = os.path.dirname(OUTPUT_FILE)
#         os.makedirs(output_dir, exist_ok=True)

#         new_df = pd.DataFrame([row_dict])
#         new_df.to_csv(
#             OUTPUT_FILE,
#             mode='a',
#             header=not os.path.exists(OUTPUT_FILE),
#             index=False
#         )
#     except Exception as e:
#         print("❌ Error saving row:", e)

# # ================= GOOGLE SEARCH =================
# def google_search(query, start):
#     url = "https://www.googleapis.com/customsearch/v1"
#     params = {
#         "key": API_KEY,
#         "cx": CX,
#         "q": query,
#         "num": 10,
#         "start": start
#     }

#     try:
#         print(f"\n🔍 Searching: {query} | Page start={start}")
#         r = requests.get(url, params=params, timeout=10)
#         r.raise_for_status()
#         data = r.json()
#         return data.get("items", [])
#     except Exception as e:
#         print("❌ Google Error:", e)
#         return []

# # ================= EXTRACT WEBSITE INFO =================
# def extract_info(url):
#     email = ""
#     address = ""
#     socials = []

#     try:
#         r = requests.get(url, headers=HEADERS, timeout=6)
#         soup = BeautifulSoup(r.text, "html.parser")
#         text = soup.get_text(" ")

#         # EMAIL
#         emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
#         if emails:
#             email = emails[0]

#         # SOCIAL LINKS
#         for a in soup.find_all("a", href=True):
#             link = a["href"]
#             if any(x in link for x in ["facebook", "linkedin", "twitter", "instagram"]):
#                 socials.append(link)

#         socials = list(set(socials))[:5]

#     except RequestException:
#         pass

#     return email, address, ", ".join(socials)

# # ================= MAIN =================
# print("🚀 USA Lead Collection Started\n")
# init_file()

# total_saved = 0

# for key in SEARCH_KEYS:
#     if time.time() - START_TIME > MAX_RUNTIME_SECONDS:
#         print("\n⏰ Time limit reached. Stopping safely...")
#         break

#     query = f"{key} company USA"
#     print(f"\n========== CATEGORY: {key} ==========")

#     # 10 pages per search: 1, 11, 21, ..., 91
#     for start in range(1, 100, 10):
#         results = google_search(query, start)

#         if not results:
#             break

#         for idx, item in enumerate(results, start=1):

#             if time.time() - START_TIME > MAX_RUNTIME_SECONDS:
#                 print("\n⏰ Time limit reached inside loop.")
#                 break

#             name = item.get("title", "").split("|")[0].strip()
#             website = item.get("link", "")

#             if not website:
#                 continue

#             print(f"   🌐 Visiting ({idx}/10): {website}")

#             email, address, socials = extract_info(website)

#             row = {
#                 "Company Name": name,
#                 "Website": website,
#                 "Email": email,
#                 "Address": address,
#                 "Social Links": socials,
#                 "Category": key,
#                 "Date Added": datetime.now().strftime("%Y-%m-%d")
#             }

#             append_row(row)
#             total_saved += 1

#             print(f"   ✅ Saved | Total: {total_saved}")
#             time.sleep(1)  # avoid API & site spam

# # ================= SUMMARY =================
# elapsed = int(time.time() - START_TIME)

# print("\n================ SUMMARY ================")
# print(f"Total Leads Saved: {total_saved}")
# print(f"Time Taken: {elapsed} seconds")
# print(f"Output File: {OUTPUT_FILE}")
# print("=========================================")


import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time
from requests.exceptions import RequestException
from urllib.parse import urljoin

# ================= CONFIG =================
API_KEY = "AIzaSyB12rbOOzlLLCC_gWR3K0zBYVIal7R-7FI"
CX = "85b02be9bcb384e72"

OUTPUT_FILE = r"C:\Users\didar\OneDrive - Startsmartz Technologies LLC\Documents\Prosaas\ProSAAS-Lead-Automation\us_leads_google_2.csv"

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


HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_RUNTIME_SECONDS = 7200
START_TIME = time.time()

CONTACT_PATHS = ["/contact", "/contact-us", "/about", "/support"]

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

OBFUSCATED_REGEX = re.compile(
    r"([a-zA-Z0-9._%+-]+)\s*(?:\[at\]|\(at\)|@)\s*"
    r"([a-zA-Z0-9.-]+)\s*(?:\[dot\]|\(dot\)|\.)\s*"
    r"([a-zA-Z]{2,})"
)

# ================= FILE INIT =================
def init_file():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    if not os.path.exists(OUTPUT_FILE):
        df = pd.DataFrame(columns=[
            "Company Name","Website","Emails","Address",
            "Facebook","LinkedIn","Twitter","Instagram",
            "Category","Date Added"
        ])
        df.to_csv(OUTPUT_FILE, index=False)

# ================= SAVE =================
def append_row(row):
    pd.DataFrame([row]).to_csv(
        OUTPUT_FILE, mode="a",
        header=not os.path.exists(OUTPUT_FILE),
        index=False
    )

# ================= GOOGLE SEARCH =================
def google_search(query, start):
    try:
        print(f"\n🔍 Searching: {query} | Page start={start}")
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key": API_KEY, "cx": CX, "q": query, "num": 10, "start": start},
            timeout=10
        )
        r.raise_for_status()
        return r.json().get("items", [])
    except Exception as e:
        print("❌ Google Error:", e)
        return []

# ================= EMAIL & SOCIAL EXTRACTION =================
def scrape_page(url, collected_emails, socials):
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ")

        # Normal emails
        collected_emails.update(EMAIL_REGEX.findall(text))

        # Obfuscated emails
        for m in OBFUSCATED_REGEX.findall(text):
            collected_emails.add(f"{m[0]}@{m[1]}.{m[2]}")

        # mailto links
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            if href.startswith("mailto:"):
                collected_emails.add(href.replace("mailto:", "").split("?")[0])

            if "facebook.com" in href and not socials["facebook"]:
                socials["facebook"] = a["href"]
            elif "linkedin.com" in href and not socials["linkedin"]:
                socials["linkedin"] = a["href"]
            elif "twitter.com" in href and not socials["twitter"]:
                socials["twitter"] = a["href"]
            elif "instagram.com" in href and not socials["instagram"]:
                socials["instagram"] = a["href"]

    except RequestException:
        pass

# ================= MAIN EXTRACT =================
def extract_info(base_url):
    collected_emails = set()
    socials = {"facebook": "", "linkedin": "", "twitter": "", "instagram": ""}

    scrape_page(base_url, collected_emails, socials)

    for path in CONTACT_PATHS:
        scrape_page(urljoin(base_url, path), collected_emails, socials)

    return ", ".join(collected_emails), socials

# ================= MAIN =================
print("🚀 USA Lead Collection Started\n")
init_file()
total_saved = 0

for key in SEARCH_KEYS:
    if time.time() - START_TIME > MAX_RUNTIME_SECONDS:
        print("\n⏰ Time limit reached. Stopping safely...")
        break

    query = f"{key} company USA"
    print(f"\n========== CATEGORY: {key} ==========")

    for start in range(1, 100, 10):
        results = google_search(query, start)
        if not results:
            break

        for idx, item in enumerate(results, start=1):
            if time.time() - START_TIME > MAX_RUNTIME_SECONDS:
                print("\n⏰ Time limit reached inside loop.")
                break

            name = item.get("title", "").split("|")[0].strip()
            website = item.get("link", "")
            if not website:
                continue

            print(f"   🌐 Visiting ({idx}/10): {website}")

            emails, socials = extract_info(website)

            append_row({
                "Company Name": name,
                "Website": website,
                "Emails": emails,
                "Address": "",
                "Facebook": socials["facebook"],
                "LinkedIn": socials["linkedin"],
                "Twitter": socials["twitter"],
                "Instagram": socials["instagram"],
                "Category": key,
                "Date Added": datetime.now().strftime("%Y-%m-%d")
            })

            total_saved += 1
            print(f"   ✅ Saved | Total: {total_saved}")
            time.sleep(1)

# ================= SUMMARY =================
elapsed = int(time.time() - START_TIME)
print("\n================ SUMMARY ================")
print(f"Total Leads Saved: {total_saved}")
print(f"Time Taken: {elapsed} seconds")
print(f"Output File: {OUTPUT_FILE}")
print("=========================================")

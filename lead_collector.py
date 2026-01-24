import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time
from requests.exceptions import RequestException

# ================= CONFIG =================
API_KEY = "AIzaSyByKO15DApLZtSsG-_KG15g6a3xtZTx6nA"
CX = "85b02be9bcb384e72"

OUTPUT_FILE = r"C:\Users\didar\Documents\Prosaas\Google search script\us_leads.xlsx"

SEARCH_QUERIES = [
    "marketing agency in {city}",
    "software company in {city}",
    "IT services company in {city}"
]

CITIES = [
    "New York NY", "Los Angeles CA", "Chicago IL", "Houston TX", "Phoenix AZ",
    "Philadelphia PA", "San Antonio TX", "San Diego CA", "Dallas TX", "San Jose CA",
    "Austin TX", "Jacksonville FL", "Fort Worth TX", "Columbus OH", "Charlotte NC",
    "San Francisco CA", "Indianapolis IN", "Seattle WA", "Denver CO", "Washington DC"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ================= FUNCTIONS =================

def google_search(query, start=1, retries=3):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "num": 10,
        "start": start
    }

    for attempt in range(1, retries + 1):
        try:
            print(f"\n🔍 Google search: {query} (start={start}) [Attempt {attempt}]")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                print("❌ Google API Error:", data["error"]["message"])
                return []

            items = data.get("items", [])
            print(f"   → {len(items)} results found")
            return items

        except RequestException as e:
            print(f"⚠️ Google request failed: {e}")
            if attempt < retries:
                time.sleep(5)
            else:
                print("❌ Skipping this query.")
                return []


def extract_email_and_location(website):
    email = ""
    location = ""

    try:
        print(f"   🌐 Visiting: {website}")
        r = requests.get(website, headers=HEADERS, timeout=6)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ")

        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            text
        )
        if emails:
            email = emails[0]

    except RequestException as e:
        print(f"   ⚠️ Website unreachable: {e}")

    return email, location


def save_data(new_df):
    # ✅ CREATE DIRECTORY IF NOT EXISTS
    output_dir = os.path.dirname(OUTPUT_FILE)
    os.makedirs(output_dir, exist_ok=True)

    if os.path.exists(OUTPUT_FILE):
        old_df = pd.read_excel(OUTPUT_FILE)
        combined = pd.concat([new_df, old_df], ignore_index=True)
        combined.drop_duplicates(subset=["Website"], inplace=True)
    else:
        combined = new_df

    combined.to_excel(OUTPUT_FILE, index=False)


# ================= MAIN SCRIPT =================

print("🚀 Lead collection started...\n")

all_new_leads = []

for city in CITIES:
    print(f"\n🏙️ Processing city: {city}")

    for query_template in SEARCH_QUERIES:
        query = query_template.format(city=city)

        for start in [1, 11, 21]:
            results = google_search(query, start=start)

            if not results:
                break

            for item in results:
                name = item.get("title", "").split("|")[0].strip()
                website = item.get("link", "")

                if not website:
                    continue

                email, location = extract_email_and_location(website)

                category = (
                    "Marketing Agency" if "marketing" in query.lower()
                    else "Software Company" if "software" in query.lower()
                    else "IT Services"
                )

                lead = {
                    "Company Name": name,
                    "Website": website,
                    "Email": email,
                    "Location": city,
                    "Category": category,
                    "Source": "Google Search",
                    "Date Added": datetime.now().strftime("%Y-%m-%d")
                }

                all_new_leads.append(lead)
                time.sleep(1)

# ================= SAVE =================

new_df = pd.DataFrame(all_new_leads)

if new_df.empty:
    print("\n⚠️ No new leads found.")
else:
    save_data(new_df)
    print(f"\n✅ Done! {len(new_df)} leads saved to:\n{OUTPUT_FILE}")

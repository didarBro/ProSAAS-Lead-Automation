"""
Lead Collection Script for CRM Email Marketing

HOW THIS SCRIPT FINDS LEADS:

1. **Source**: Google Maps Places API (Text Search & Place Details)
   - Searches for businesses using queries like "marketing agency in New York NY"
   - Can be extended to any industry or city

2. **Collected Info**:
   - Company Name
   - Website
   - Email (scraped from website if available)
   - Location (City)
   - Category (Google place types)
   - Source ("Google Maps")
   - Date Added

3. **Strategy for more leads**:
   - Expand SEARCH_QUERIES with more industry keywords.
   - Add more CITIES (or zip codes) for detailed location coverage.
   - Increase API call limits or batch processing to fetch more results per query.
   - Scrape multiple pages (Google Maps supports pagination with `next_page_token`) for deeper coverage.
   - Use company websites and LinkedIn for additional emails.

4. **CRM Integration**:
   - This script generates an Excel file `google_map_leads.xlsx`
   - Can be imported into any CRM
   - Emails can be validated externally before marketing campaigns

5. **Safety / Best Practices**:
   - Limits top 5 results per query to avoid API quota issues
   - Sleep between requests to prevent throttling
   - Saves partially collected data if an error occurs
"""

import requests
import pandas as pd
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep

# ================= CONFIG =================
API_KEY = "YOUR_GOOGLE_API_KEY"  # Replace with your actual API key
OUTPUT_FILE = "google_map_leads.xlsx"

SEARCH_QUERIES = [
    "marketing agency",
    "software company",
    "IT services company",
    # Add more queries for better coverage
    "digital marketing",
    "web development",
    "SEO agency",
    "cloud services",
]

CITIES = [
    "New York NY", "Los Angeles CA", "Chicago IL", "Houston TX", "Phoenix AZ",
    "Philadelphia PA", "San Antonio TX", "San Diego CA", "Dallas TX", "San Jose CA",
    "Austin TX", "Jacksonville FL", "Fort Worth TX", "Columbus OH", "Charlotte NC",
    "San Francisco CA", "Indianapolis IN", "Seattle WA", "Denver CO", "Washington DC",
    # Add more cities or regions as needed
]

HEADERS = {"User-Agent": "Mozilla/5.0"}


# ================= FUNCTIONS =================

def get_email_from_website(url):
    """Scrape the first email from a website"""
    if not url:
        return ""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        return emails[0] if emails else ""
    except Exception:
        return ""


def load_existing_leads():
    """Load existing Excel file if it exists"""
    if os.path.exists(OUTPUT_FILE):
        return pd.read_excel(OUTPUT_FILE)
    return pd.DataFrame()


def save_leads(leads):
    """Save leads to Excel and create the file if it's the first run"""
    df_existing = load_existing_leads()
    df_new = pd.DataFrame(leads)

    combined_df = pd.concat([df_existing, df_new], ignore_index=True)
    combined_df.drop_duplicates(subset=["Company Name", "Website"], inplace=True)

    folder = os.path.dirname(OUTPUT_FILE)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    combined_df.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ {len(df_new)} leads saved/updated in {OUTPUT_FILE}")


def search_places(query):
    """Search Google Maps Places API for businesses matching the query"""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": API_KEY,
        "region": "us",
        "type": "establishment",
    }
    response = requests.get(url, params=params).json()
    if response.get("status") != "OK":
        print(f"⚠️ No results or error for query '{query}': {response.get('status')}")
        return []
    return response.get("results", [])


def get_place_details(place_id):
    """Get detailed info about a business from Google Places"""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,website,types,formatted_address,formatted_phone_number",
        "key": API_KEY,
    }
    response = requests.get(url, params=params).json()
    return response.get("result", {})


def collect_leads():
    """Main function to collect leads and save them"""
    collected_leads = []

    for city in CITIES:
        print(f"\n🏙️ Processing city: {city}")

        for query_template in SEARCH_QUERIES:
            query = f"{query_template} in {city}"
            print(f"🔍 Searching: {query}")

            try:
                results = search_places(query)
                if not results:
                    continue

                for place in results[:10]:  # Increase top results for more leads
                    details = get_place_details(place["place_id"])

                    name = details.get("name", "")
                    website = details.get("website", "")
                    category = ", ".join(details.get("types", []))
                    email = get_email_from_website(website)
                    phone = details.get("formatted_phone_number", "")

                    lead = {
                        "Company Name": name,
                        "Website": website,
                        "Email": email,
                        "Phone": phone,
                        "Location": city,
                        "Category": category,
                        "Source": "Google Maps",
                        "Date Added": datetime.now().strftime("%Y-%m-%d"),
                    }

                    collected_leads.append(lead)
                    print(f"✅ Collected: {name} | {email} | {phone}")

                    sleep(1)  # Avoid throttling

            except Exception as e:
                print(f"❌ Error occurred: {e}")
                if collected_leads:
                    save_leads(collected_leads)
                return

    if collected_leads:
        save_leads(collected_leads)
    print("🎉 Lead collection completed!")


# ================= MAIN =================
if __name__ == "__main__":
    collect_leads()

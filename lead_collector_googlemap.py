import requests
import pandas as pd
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep

# ================= CONFIG =================
API_KEY = "AIzaSyCYNwoHn7jZbCaf7-Il0utAM8Frp0_Tm0w"  # Replace with your actual Google API key
OUTPUT_FILE = "google_map_leads.xlsx"

SEARCH_QUERIES = [
    "marketing agency",
    "software company",
    "IT services company"
]

CITIES = [
    "New York NY", "Los Angeles CA", "Chicago IL", "Houston TX", "Phoenix AZ",
    "Philadelphia PA", "San Antonio TX", "San Diego CA", "Dallas TX", "San Jose CA",
    "Austin TX", "Jacksonville FL", "Fort Worth TX", "Columbus OH", "Charlotte NC",
    "San Francisco CA", "Indianapolis IN", "Seattle WA", "Denver CO", "Washington DC"
]

HEADERS = {"User-Agent": "Mozilla/5.0"}


# ================= FUNCTIONS =================

def get_email_from_website(url):
    """Try to scrape email from a website"""
    if not url:
        return ""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        return emails[0] if emails else ""
    except:
        return ""


def load_existing_leads():
    """Load existing Excel file if exists"""
    if os.path.exists(OUTPUT_FILE):
        return pd.read_excel(OUTPUT_FILE)
    return pd.DataFrame()


def save_leads(leads):
    """Save leads to Excel, create file if first run"""
    df_existing = load_existing_leads()
    df_new = pd.DataFrame(leads)

    combined_df = pd.concat([df_existing, df_new], ignore_index=True)
    combined_df.drop_duplicates(subset=["Company Name", "Website"], inplace=True)

    # Ensure folder exists
    folder = os.path.dirname(OUTPUT_FILE)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    combined_df.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ {len(df_new)} leads saved/updated in {OUTPUT_FILE}")


def search_places(query):
    """Search Google Maps Places API for a query"""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": API_KEY,
        "region": "us",
        "type": "establishment"
    }
    response = requests.get(url, params=params).json()
    if response.get("status") != "OK":
        print(f"⚠️ No results or error for query '{query}': {response.get('status')}")
        return []
    return response.get("results", [])


def get_place_details(place_id):
    """Get place details including website"""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,website,types",
        "key": API_KEY
    }
    response = requests.get(url, params=params).json()
    return response.get("result", {})


def collect_leads():
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

                # Limit top 5 results per query to save API quota
                for place in results[:5]:
                    details = get_place_details(place["place_id"])

                    name = details.get("name", "")
                    website = details.get("website", "")
                    category = ", ".join(details.get("types", []))
                    email = get_email_from_website(website)

                    lead = {
                        "Company Name": name,
                        "Website": website,
                        "Email": email,
                        "Location": city,
                        "Category": category,
                        "Source": "Google Maps",
                        "Date Added": datetime.now().strftime("%Y-%m-%d")
                    }

                    collected_leads.append(lead)
                    print(f"✅ Collected: {name}")

                    sleep(1)  # avoid API throttling

            except Exception as e:
                print(f"❌ Error occurred: {e}")
                if collected_leads:
                    save_leads(collected_leads)  # save partial results
                return

    if collected_leads:
        save_leads(collected_leads)
    print("🎉 Lead collection completed!")


# ================= MAIN =================
if __name__ == "__main__":
    collect_leads()

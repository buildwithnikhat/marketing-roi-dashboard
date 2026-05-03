# ingestion/extractor.py
# Real API data collection — professional patterns

import requests
import pandas as pd
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("  API DATA COLLECTION")
print("=" * 60)

# ─────────────────────────────────────────────────────
# WHAT IS AN API?
#
# API = Application Programming Interface
# Think of it like a waiter in a restaurant:
#
#   You (Python) → place order (HTTP request) → Waiter (API)
#   Waiter (API) → brings food (JSON data)    → You (Python)
#
# Every marketing platform has an API:
#   Google Ads API  → your campaign data
#   Meta Ads API    → your Facebook/Instagram data
#   HubSpot API     → your CRM data
#
# We use FREE public APIs to learn the same patterns
# ─────────────────────────────────────────────────────

class APICollector:
    """
    Professional API collector with:
    - Automatic retry on failure
    - Rate limit handling
    - Timeout protection
    - Full error logging
    """

    def __init__(self):
        # Session reuses connection — faster than new connection each time
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MarketingROIDashboard/1.0',
            'Accept':     'application/json',
        })
        self.results = {}

    def safe_get(self, url: str, params: dict = None,
                 max_retries: int = 3) -> dict:
        """
        Makes API call with retry logic.

        Why retry?
        → APIs fail sometimes (network issues, server busy)
        → Production systems NEVER give up on first failure
        → We wait longer each retry (exponential backoff)
        """
        for attempt in range(max_retries):
            try:
                print(f"   📡 Calling: {url[:60]}...")
                response = self.session.get(
                    url,
                    params=params,
                    timeout=10       # Never wait more than 10 seconds
                )

                if response.status_code == 200:
                    print(f"   ✅ Success! Status: 200")
                    return response.json()

                elif response.status_code == 429:
                    wait = 2 ** attempt
                    print(f"   ⚠️  Rate limited. Waiting {wait}s...")
                    time.sleep(wait)

                elif response.status_code == 404:
                    print(f"   ❌ Not found (404): {url}")
                    return None

                else:
                    print(f"   ❌ Error {response.status_code}")
                    return None

            except requests.exceptions.Timeout:
                print(f"   ⏱️  Timeout — attempt {attempt+1}/{max_retries}")
                time.sleep(2 ** attempt)

            except requests.exceptions.ConnectionError:
                print(f"   🔌 No internet — attempt {attempt+1}/{max_retries}")
                time.sleep(2 ** attempt)

            except Exception as e:
                print(f"   ❌ Unexpected error: {e}")
                return None

        print(f"   ❌ All {max_retries} attempts failed")
        return None

    # ─────────────────────────────────────────────────
    # API 1: Exchange Rates
    # Real use: campaigns run in multiple currencies
    # We convert all spend to INR for unified reporting
    # ─────────────────────────────────────────────────

    def get_exchange_rates(self) -> dict:
        print("\n💱 API 1: Fetching exchange rates...")
        url  = "https://open.er-api.com/v6/latest/USD"
        data = self.safe_get(url)

        if data and data.get('result') == 'success':
            rates = {
                'USD': 1.0,
                'INR': data['rates'].get('INR', 83.5),
                'EUR': data['rates'].get('EUR', 0.92),
                'GBP': data['rates'].get('GBP', 0.79),
                'AED': data['rates'].get('AED', 3.67),
            }
        else:
            # Fallback rates if API fails
            print("   ⚠️  Using fallback rates")
            rates = {'USD':1.0, 'INR':83.5, 'EUR':0.92,
                     'GBP':0.79, 'AED':3.67}

        print(f"   💰 Rates fetched:")
        for currency, rate in rates.items():
            print(f"      1 USD = {rate} {currency}")

        self.results['exchange_rates'] = rates
        return rates

    # ─────────────────────────────────────────────────
    # API 2: Country/Region Data
    # Real use: campaigns target specific countries
    # Geographic data helps analyze campaign reach
    # ─────────────────────────────────────────────────

    def get_country_data(self) -> pd.DataFrame:
        print("\n🌍 API 2: Fetching country data...")
        url  = "https://restcountries.com/v3.1/region/asia"
        data = self.safe_get(url)

        if not data:
            print("   ⚠️  Using fallback country data")
            return pd.DataFrame([
                {'country': 'India',     'population': 1400000000, 'currency': 'INR'},
                {'country': 'Pakistan',  'population': 220000000,  'currency': 'PKR'},
                {'country': 'Singapore', 'population': 5800000,    'currency': 'SGD'},
            ])

        countries = []
        for c in data:
            currencies = list(c.get('currencies', {}).keys())
            countries.append({
                'country':    c.get('name', {}).get('common', 'Unknown'),
                'region':     c.get('region', ''),
                'subregion':  c.get('subregion', ''),
                'population': c.get('population', 0),
                'currency':   currencies[0] if currencies else 'Unknown',
                'area_km2':   c.get('area', 0),
            })

        df = pd.DataFrame(countries)
        print(f"   ✅ {len(df)} countries fetched")
        print(f"   Sample: {df['country'].head(5).tolist()}")
        self.results['countries'] = df
        return df

    # ─────────────────────────────────────────────────
    # API 3: Simulated Campaign Data
    # Real use: this is exactly how Google Ads API
    # and Meta Ads API return data — as JSON objects
    # ─────────────────────────────────────────────────

    def get_simulated_campaigns(self) -> pd.DataFrame:
        print("\n📊 API 3: Fetching simulated campaign data...")
        campaigns = []

        # Fetch 10 records — simulates paginated API response
        for post_id in range(1, 11):
            url  = f"https://jsonplaceholder.typicode.com/posts/{post_id}"
            data = self.safe_get(url)

            if data:
                # This transformation is EXACTLY what you do
                # with real Google Ads or Meta API responses
                campaigns.append({
                    'campaign_id':   f"API_CAMP_{data['id']:04d}",
                    'campaign_name': data['title'][:50],
                    'description':   data['body'][:80],
                    'user_id':       data['userId'],
                    'source':        'api_collected',
                    'collected_at':  datetime.now().isoformat(),
                })
                time.sleep(0.3)   # Polite delay between requests

        df = pd.DataFrame(campaigns)
        print(f"   ✅ {len(df)} campaigns fetched from API")
        self.results['api_campaigns'] = df
        return df

    def save_all(self, rates, countries, campaigns):
        """Save all API data to data/raw/"""
        os.makedirs("data/raw", exist_ok=True)

        # Save exchange rates as JSON
        with open("data/raw/api_exchange_rates.json", "w") as f:
            json.dump({
                'rates':        rates,
                'collected_at': datetime.now().isoformat(),
                'source':       'open.er-api.com'
            }, f, indent=2)
        print(f"\n💾 Saved: data/raw/api_exchange_rates.json")

        # Save country data as CSV
        if not countries.empty:
            countries.to_csv("data/raw/api_countries.csv", index=False)
            print(f"💾 Saved: data/raw/api_countries.csv")

        # Save API campaigns as CSV
        if not campaigns.empty:
            campaigns.to_csv("data/raw/api_campaigns.csv", index=False)
            print(f"💾 Saved: data/raw/api_campaigns.csv")


# ── MAIN ─────────────────────────────────────────────
if __name__ == "__main__":
    collector = APICollector()

    rates     = collector.get_exchange_rates()
    countries = collector.get_country_data()
    campaigns = collector.get_simulated_campaigns()

    collector.save_all(rates, countries, campaigns)

    print("\n" + "=" * 60)
    print("  ✅ API COLLECTION COMPLETE")
    print(f"  Exchange rates:  {len(rates)} currencies")
    print(f"  Countries:       {len(countries)} records")
    print(f"  API campaigns:   {len(campaigns)} records")
    print(f"  All saved to:    data/raw/")
    print("=" * 60)
import os
import argparse
import time
import pandas as pd
import requests
from dotenv import load_dotenv
from typing import List, Dict, Optional

# --- Configuration ---
load_dotenv()

# --- Data Collection Logic (Functional) ---

def get_api_credentials() -> Optional[Dict[str, str]]:
    """Retrieves Algolia credentials from environment variables."""
    app_id = os.getenv("ALGOLIA_APP_ID")
    api_key = os.getenv("ALGOLIA_API_KEY")
    index_name = os.getenv("ALGOLIA_INDEX", "products")
    
    if not all([app_id, api_key]):
        print("[!] Error: Missing ALGOLIA_APP_ID or ALGOLIA_API_KEY in .env")
        return None
    
    return {
        "app_id": app_id,
        "api_key": api_key,
        "index": index_name
    }

def build_filters(founders_code: bool, min_revenue: int) -> str:
    """Constructs a SQL-like filter string for the Algolia search query."""
    parts = []
    if founders_code:
        parts.append("_tags:founders-code-yes")
    if min_revenue > 0:
        parts.append(f"revenue >= {min_revenue}")
    
    return " AND ".join(parts)

def fetch_page(session: requests.Session, app_id: str, index: str, page: int, filters: str, per_page: int) -> Optional[Dict]:
    """Fetches a single page of results from the Algolia index."""
    url = f"https://{app_id}-dsn.algolia.net/1/indexes/{index}/query"
    payload = {
        "query": "",
        "hitsPerPage": per_page,
        "page": page,
        "filters": filters
    }
    
    try:
        response = session.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[!] Network error on page {page}: {e}")
        return None

def collect_data(creds: Dict[str, str], founders_code: bool, min_revenue: int, max_pages: int) -> List[Dict]:
    """Orchestrates the data collection loop across multiple pages."""
    all_hits = []
    filters = build_filters(founders_code, min_revenue)
    
    print(f"[*] Starting collection | Filters: [{filters if filters else 'None'}]")
    
    # We use a session for connection pooling and slightly better performance
    with requests.Session() as session:
        session.headers.update({
            "X-Algolia-API-Key": creds["api_key"],
            "X-Algolia-Application-Id": creds["app_id"],
            "Content-Type": "application/json",
            "User-Agent": "IndieHackers-Data-Collector/2.0"
        })
        
        for page in range(max_pages):
            data = fetch_page(session, creds["app_id"], creds["index"], page, filters, 100)
            if not data:
                break
                
            hits = data.get("hits", [])
            if not hits:
                print("[*] Reached the end of available data index.")
                break
                
            all_hits.extend(hits)
            print(f"[+] Processing page {page} | Found {len(hits)} items.")
            
            # Respectful delay between requests
            time.sleep(1)
            
            # Stop if we hit the total number of pages available
            if page >= data.get("nbPages", 0) - 1:
                print("[*] Reached the last possible page in Algolia.")
                break
                
    return all_hits

def export_results(hits: List[Dict], output_file: str):
    """Processes raw data into a clean CSV format using pandas."""
    if not hits:
        print("[!] Warning: No data found matching your filters. Export skipped.")
        return

    processed = []
    for hit in hits:
        processed.append({
            "Name": hit.get("name", "N/A"),
            "Tagline": hit.get("tagline", ""),
            "Monthly Revenue ($)": hit.get("revenue", 0),
            "IndieHackers URL": f"https://www.indiehackers.com/product/{hit.get('objectID', '')}",
            "Website": hit.get("websiteUrl", ""),
            "Status": hit.get("status", "unknown")
        })

    try:
        df = pd.DataFrame(processed)
        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"[SUCCESS] Exported {len(processed)} products to {output_file}")
    except Exception as e:
        print(f"[!] Export failed during file writing: {e}")

# --- CLI Entry Point ---

def main():
    """Main execution function that handles CLI arguments."""
    parser = argparse.ArgumentParser(
        description="IndieHackers Data Collector (Professional functional version)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--revenue", type=int, default=1, help="Minimum monthly revenue to filter by")
    parser.add_argument("--no-code", action="store_true", help="Include products without the 'Founders Code' tag")
    parser.add_argument("--pages", type=int, default=5, help="Maximum number of pages to fetch (100 per page)")
    parser.add_argument("--output", type=str, default="products.csv", help="The filename for the output CSV")
    
    args = parser.parse_args()
    
    # Load and validate credentials layer
    creds = get_api_credentials()
    if not creds:
        return

    # Execute main workflow
    results = collect_data(
        creds=creds,
        founders_code=not args.no_code,
        min_revenue=args.revenue,
        max_pages=args.pages
    )
    
    export_results(results, args.output)

if __name__ == "__main__":
    main()

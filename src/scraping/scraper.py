import requests
from bs4 import BeautifulSoup
import time
import os
import json
from datetime import datetime

HEADERS = {
    "User-Agent": "ResearchBot/1.0"
}
RAW_HTML_DIR = "data/raw/html"
SCRAPED_JSON_DIR = "data/raw/scraped"

os.makedirs(RAW_HTML_DIR, exist_ok=True)
os.makedirs(SCRAPED_JSON_DIR, exist_ok=True)

def scrape_single_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        save_html("single_page.html", response.text)
        
        soup = BeautifulSoup(response.text, "lxml")
        rows = soup.select("tr.team")
        
        results = []
        for row in rows:
            record = {
                "name":   row.select_one("td.name").get_text(strip=True) if row.select_one("td.name") else "",
                "year":   row.select_one("td.year").get_text(strip=True) if row.select_one("td.year") else "",
                "wins":   row.select_one("td.wins").get_text(strip=True) if row.select_one("td.wins") else "",
                "losses": row.select_one("td.losses").get_text(strip=True) if row.select_one("td.losses") else "",
                "source": url,
                "type": "scraped_static",
                "timestamp": datetime.now().isoformat()
            }
            results.append(record)
        return results
    except Exception as e:
        print(f"Error in single page scrape: {e}")
        return []

def scrape_multiple_pages(base_url, max_pages=3):
    all_results = []
    
    for page in range(1, max_pages + 1):
        url = f"{base_url}?page_num={page}"
        print(f"Scraping page {page}: {url}")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            response.raise_for_status()
            
            file_name = f"teams_page_{page}.html"
            save_html(file_name, response.text)
            
            soup = BeautifulSoup(response.text, "lxml")
            rows = soup.select("tr.team")
            
            for row in rows:
                record = {
                    "name":    row.select_one("td.name").get_text(strip=True) if row.select_one("td.name") else "",
                    "year":    row.select_one("td.year").get_text(strip=True) if row.select_one("td.year") else "",
                    "wins":    row.select_one("td.wins").get_text(strip=True) if row.select_one("td.wins") else "",
                    "losses":  row.select_one("td.losses").get_text(strip=True) if row.select_one("td.losses") else "",
                    "win_pct": row.select_one("td.pct").get_text(strip=True) if row.select_one("td.pct") else "",
                    "page_scraped": page,
                    "source": url,
                    "type": "scraped_multi",
                    "file_name": file_name,
                    "timestamp": datetime.now().isoformat()
                }
                all_results.append(record)
            
            time.sleep(1.5) 
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
    
    save_json("teams_multiple_pages.json", all_results)
    return all_results

def scrape_oscar_films(years=None):
    if years is None:
        years = [2015]
    
    base_url = "https://www.scrapethissite.com/pages/ajax-javascript/"
    all_films = []
    
    for year in years:
        url = f"{base_url}?ajax=true&year={year}"
        print(f"Fetching API data for year: {year}...")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            response.raise_for_status()
            
            films = response.json()  
            
            for film in films:
                film["year_scraped"] = year
                film["source"] = url
                film["type"] = "scraped_api"
                film["timestamp"] = datetime.now().isoformat()
                all_films.append(film)
            
            time.sleep(1)
        except Exception as e:
            print(f"Error fetching Oscar year {year}: {e}")
    
    save_json("oscar_films.json", all_films)
    return all_films

def save_html(filename, html_text):
    path = os.path.join(RAW_HTML_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_text)

def save_json(filename, data):
    path = os.path.join(SCRAPED_JSON_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def scrape_hub_artworks(start_id, end_id):
    all_artworks = []
    
    for art_id in range(start_id, end_id + 1):
        url = f"https://thehub.ba/artwork/{art_id}"
        print(f"Scraping artwork {art_id}: {url}")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            response.raise_for_status()
            
            file_name = f"artwork_{art_id}.html"
            save_html(file_name, response.text)
            
            soup = BeautifulSoup(response.text, "lxml")
            
            title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "N/A"
            
            record = {
                "title": title,
                "artwork_id": art_id,
                "source": url,
                "type": "scraped",
                "file_name": file_name,
                "timestamp": datetime.now().isoformat()
            }
            
            all_artworks.append(record)
            
        except Exception as e:
            print(f"Error scraping ID {art_id}: {e}")
            
        time.sleep(1.5)
    
    print(f"Successfully scraped {len(all_artworks)} items")
    save_json("hub_artworks.json", all_artworks)
    return all_artworks

if __name__ == "__main__":
    results = scrape_hub_artworks(31, 33)
    for item in results:
        print(item)

    print("--- Starting Hockey Scrape ---")
    teams_url = "https://www.scrapethissite.com/pages/forms/"
    teams_data = scrape_multiple_pages(teams_url, max_pages=2)
    
    print("\n--- Starting Oscar API Scrape ---")
    oscar_data = scrape_oscar_films(years=[2014, 2015])
    
    print("\nScraping complete. Check the 'data/raw/' folders.")
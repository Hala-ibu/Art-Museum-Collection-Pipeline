import requests
import os
import json
from dotenv import load_dotenv
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import logger

load_dotenv()
BASE_URL = os.getenv("AIC_BASE_URL")

def fetch_artworks(pages=3):
    logger.info(f"Starting API acquisition from {BASE_URL}")
    all_pages_data = []

    for page in range(1, pages + 1):
        try:
            params = {"page": page, "limit": 10}
            response = requests.get(BASE_URL, params=params)
            
            response.raise_for_status() 
            
            data = response.json()
            all_pages_data.append(data)

            file_path = f"data/raw/api/artworks_page_{page}.json"
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            
            logger.info(f"Successfully saved page {page} to {file_path}")

        except Exception as e:
            logger.error(f"Error fetching page {page}: {e}")
            
    return all_pages_data

if __name__ == "__main__":
    fetch_artworks(3)
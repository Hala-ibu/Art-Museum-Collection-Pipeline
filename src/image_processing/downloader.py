import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

CMA_API_URL = "https://openaccess-api.clevelandart.org/api/artworks/"

def fetch_cma_art_data(limit=10):
    try:
        url = f"{CMA_API_URL}?has_image=1&limit={limit}"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get('data', [])
    except Exception as e:
        logger.error(f"Error: {e}")
        return []

def download_cma_image(image_url, image_id, dest_dir):
    if not image_url:
        return None
    
    dest_path = Path(dest_dir) / f"{image_id}.jpg"
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if dest_path.exists():
        return str(dest_path)

    try:
        resp = requests.get(image_url, stream=True, timeout=20)
        resp.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return str(dest_path)
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None

def download_collection_images(artworks, dest_dir='data/raw/images'):
    downloaded_records = []
    for art in artworks:
        image_info = art.get('images', {}).get('web', {})
        image_url = image_info.get('url')
        image_id = art.get('id')
        
        if image_url and image_id:
            local_file = download_cma_image(image_url, image_id, dest_dir)
            if local_file:
                downloaded_records.append({
                    'artwork_id': image_id,
                    'title': art.get('title'),
                    'local_path': local_file,
                    'source': 'cleveland_museum_api',
                    'timestamp': time.strftime("%Y-%m-%dT%H:%M:%S")
                })
        time.sleep(0.2)
    return downloaded_records

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    art_list = fetch_cma_art_data(limit=10)
    results = download_collection_images(art_list)
    for res in results:
        print(res)
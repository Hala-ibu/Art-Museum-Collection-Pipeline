import os
import sys
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import logger

client = MongoClient("mongodb://localhost:27017/")
db = client["Art-Museum-Collection-Pipeline"]
collection = db["art_collection_data"]

def save_to_mongo(data, source, content_type, file_name=None, extra_metadata=None):
    try:
        document = {
            "data": data,
            "source": source,
            "type": content_type,            
            "file_name": file_name,           
            "timestamp": datetime.utcnow(), 
            "version": 1
        }
        if extra_metadata:
            document.update(extra_metadata)

        result = collection.insert_one(document)
        logger.info(f"MongoDB Insert Successful: ID {result.inserted_id} | Type: {content_type}")
        return result.inserted_id
    except Exception as e:
        logger.error(f"MongoDB Insertion Failed: {e}")

def build_image_record(image_meta):
    return {
        "data": {
            "dimensions": f"{image_meta.get('width')}x{image_meta.get('height')}",
            "aspect_ratio": image_meta.get('aspect_ratio'),
            "format": image_meta.get('format'),
            "file_size_kb": image_meta.get('file_size_kb'),
            "paths": {
                "original": image_meta.get('original_path'),
                "resized": image_meta.get('resized_path'),
                "thumbnail": image_meta.get('thumbnail_path'),
                "webp": image_meta.get('webp_path')
            },
            "exif": image_meta.get('exif')
        },
        "source": "Cleveland Museum of Art API",
        "file_name": image_meta.get('filename'),
        "type": "image_processing"
    }

def build_scraped_record(data, source_url, page_number=None, file_name=None):
    return {
        "data": data,
        "source": source_url,
        "page_number": page_number,
        "file_name": file_name,               
        "extracted_at": datetime.utcnow(),
        "type": "web_scraping"
    }

def build_ocr_record(text, source_file, page_number=None):
    return {
        "data": {"text": text},
        "source": source_file,
        "page_number": page_number,
        "extracted_at": datetime.utcnow(),
        "type": "ocr"
    }
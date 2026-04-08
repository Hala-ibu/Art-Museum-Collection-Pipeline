from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os
import sys

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

        logger.info(
            f"MongoDB Insert Successful: ID {result.inserted_id} | Type: {content_type}"
        )

    except Exception as e:
        logger.error(f"MongoDB Insertion Failed: {e}")



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



if __name__ == "__main__":
    test_data = {"item": "Test Artwork", "artist": "Test Artist"}

    record = build_scraped_record(
        data=test_data,
        source_url="http://test-url.com",
        page_number=1,
        file_name="test_file.html"
    )

    save_to_mongo(
        data=record["data"],
        source=record["source"],
        content_type=record["type"],
        file_name=record["file_name"],
        extra_metadata={
            "page_number": record["page_number"],
            "extracted_at": record["extracted_at"]
        }
    )
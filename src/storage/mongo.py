import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Connect to your logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import logger

load_dotenv()

def save_to_mongo(data, collection_name):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["art_institute_db"]
        collection = db[collection_name]
        
        if isinstance(data, list):
            collection.insert_many(data)
        else:
            collection.insert_one(data)
            
        logger.info(f"Successfully saved data to MongoDB collection: {collection_name}")
        
    except Exception as e:
        logger.error(f"Failed to save to MongoDB: {e}")

if __name__ == "__main__":
    test_data = {"test": "connection", "project": "Art Institute"}
    save_to_mongo(test_data, "test_collection")
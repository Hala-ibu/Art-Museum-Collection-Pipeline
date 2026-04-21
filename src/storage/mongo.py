import os
import logging
from datetime import datetime
from pathlib import Path
from PIL import Image
from pymongo import MongoClient
from datetime import timezone

client = MongoClient("mongodb://localhost:27017/")
db = client["Art-Museum-Collection-Pipeline"]

art_collection = db["art_collection_data"]
image_metadata_collection = db["image_metadata"]
transcripts_collection = db["transcripts"]

logger = logging.getLogger(__name__)

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

        result = art_collection.insert_one(document)
        logger.info(f"MongoDB Insert Successful: ID {result.inserted_id} | Type: {content_type}")
        return result.inserted_id
    except Exception as e:
        logger.error(f"MongoDB Insertion Failed: {e}")

def apply_image_metadata(image_path, movie_id=None):
    img = Image.open(image_path)
    width, height = img.size
    file_size = os.path.getsize(image_path)

    return {
        'filename': Path(image_path).name,
        'movie_id': movie_id,
        'width': width,
        'height': height,
        'file_size': file_size,
        'format': img.format
    }

def get_db():
    return db

def process_images_and_save_metadata(image_paths, movie_id=None):
    metadata_list = []
    for image_path in image_paths:
        img_metadata = apply_image_metadata(image_path, movie_id)
        metadata_list.append(img_metadata)
    save_image_metadata(metadata_list)
    

def save_image_metadata(metadata_list):
    for meta in metadata_list:
        meta['processed_at'] = datetime.now(timezone.utc).isoformat()
        image_metadata_collection.update_one(
            {'filename': meta['filename']},  
            {'$set': meta},  
            upsert=True  
        )
    print(f'Saved {len(metadata_list)} image records to MongoDB')

def save_transcript(transcript_result, source_path, source_type='audio'):

    doc = {
        'source_file': Path(source_path).name,
        'source_path': str(source_path),
        'source_type': source_type,
        'model': transcript_result.get('model', 'base'),
        'language': transcript_result.get('language', 'en'),
        'duration_s': transcript_result.get('duration_s', 0),
        'full_text': transcript_result.get('full_text', ''),
        'segments': transcript_result.get('segments', []), 
        'transcribed_at': datetime.utcnow().isoformat(),
    }
    
    result = transcripts_collection.insert_one(doc)
    logger.info(f'Saved transcript to MongoDB: {doc["source_file"]} (id={result.inserted_id})')
    return str(result.inserted_id)

if __name__ == "__main__":
    images_dir = Path('data/raw/images')
    if images_dir.exists():
        image_paths = [str(f) for f in images_dir.glob('*') if f.suffix.lower() in ['.png', '.jpg', '.jpeg']]
        if image_paths:
            metadata_list = [apply_image_metadata(p, movie_id="museum_collection_001") for p in image_paths]
            save_image_metadata(metadata_list)

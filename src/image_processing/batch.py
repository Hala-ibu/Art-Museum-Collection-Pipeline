import json
import sys
import os
from pathlib import Path
from tqdm import tqdm
import logging

from processor import inspect_image, generate_thumbnail, resize_proportional, convert_to_webp
from exif_utils import get_exif_summary

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(PROJECT_ROOT)

try:
    from src.storage.mongo import save_to_mongo, build_image_record
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage')))
    from mongo import save_to_mongo, build_image_record

try:
    from src.utils.upload_utils import upload_batch
except ImportError:
    def upload_batch(data): pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', 
                    handlers=[logging.FileHandler('pipeline.log'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.gif'}

def _process_single(img_path, output_dir, max_width, thumb_size, convert_webp, extract_metadata):
    stem = img_path.stem
    meta = inspect_image(img_path)

    resized_path = output_dir / 'resized' / f'{stem}_resized.jpg'
    resize_proportional(img_path, resized_path, max_width=max_width)
    meta['resized_path'] = str(resized_path)

    thumb_path = output_dir / 'thumbnails' / f'{stem}_thumb.jpg'
    generate_thumbnail(img_path, thumb_path, max_size=thumb_size)
    meta['thumbnail_path'] = str(thumb_path)

    if convert_webp:
        webp_path = output_dir / 'webp' / f'{stem}.webp'
        convert_to_webp(img_path, webp_path)
        meta['webp_path'] = str(webp_path)

    if extract_metadata:
        meta['exif'] = get_exif_summary(img_path)

    meta['original_path'] = str(img_path)
    meta['filename'] = img_path.name
    return meta

def batch_process_images(input_dir, output_dir, max_width=500, thumb_size=(128, 128), convert_webp=True, extract_metadata=True):
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    
    for folder in ['resized', 'thumbnails', 'webp']:
        (output_dir / folder).mkdir(parents=True, exist_ok=True)

    files = [f for f in input_dir.rglob('*') if f.suffix.lower() in SUPPORTED]
    logger.info(f'Batch processing {len(files)} images from {input_dir}')

    results, errors = [], []
    for img_path in tqdm(files, desc='Processing images'):
        try:
            meta = _process_single(img_path, output_dir, max_width, thumb_size, convert_webp, extract_metadata)
            
            record = build_image_record(meta)
            save_to_mongo(
                data=record["data"], 
                source=record["source"], 
                content_type=record["type"], 
                file_name=img_path.name
            )
            
            results.append(meta)
        except Exception as e:
            logger.error(f'Failed: {img_path.name} - {e}')
            errors.append({'file': str(img_path), 'error': str(e)})

    if results:
        upload_batch(results)

    return results, errors

if __name__ == "__main__":
    results, errors = batch_process_images(
        input_dir='data/raw/images', 
        output_dir='data/processed'
    )
    
    print(f'Batch complete. Success: {len(results)}, Errors: {len(errors)}')
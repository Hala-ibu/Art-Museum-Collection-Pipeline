import os
import logging
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

logger = logging.getLogger(__name__)

def extract_exif(path):
    img = Image.open(path)
    exif_data = img.getexif()
    if not exif_data:
        logger.warning(f'No EXIF data found in {path}')
        return {}
    result = {}
    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, str(tag_id))
        if isinstance(value, bytes):
            value = value.decode('utf-8', errors='replace')
        result[tag_name] = value
    return result

def extract_gps(path):
    img = Image.open(path)
    exif_data = img.getexif()
    if not exif_data:
        return None
    gps_ifd = exif_data.get_ifd(0x8825)
    if not gps_ifd:
        return None
    gps = {}
    for key, val in gps_ifd.items():
        gps[GPSTAGS.get(key, key)] = val
    return gps

def get_exif_summary(path):
    exif = extract_exif(path)
    gps = extract_gps(path)
    return {
        'camera_make': exif.get('Make'),
        'camera_model': exif.get('Model'),
        'date_taken': exif.get('DateTimeOriginal') or exif.get('DateTime'),
        'exposure': str(exif.get('ExposureTime')),
        'aperture': str(exif.get('FNumber')),
        'iso': exif.get('ISOSpeedRatings'),
        'focal_length': str(exif.get('FocalLength')),
        'orientation': exif.get('Orientation'),
        'gps': gps,
    }

def strip_exif(path, output_path):
    img = Image.open(path)
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    clean.save(output_path)
    logger.info(f'EXIF stripped: {output_path}')
    return output_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    photo1_path = "data/raw/exif_samples/IMG20260330174456.jpg"
    photo2_path = "data/raw/exif_samples/Screenshot_2026-04-07-15-37-42-91_50ef9f5a0f3fc24b6f0ffc8843167fe4.jpg"
    if os.path.exists(photo1_path):
        summary = get_exif_summary(photo1_path)
        print(summary)
    if os.path.exists(photo2_path):
        summary = get_exif_summary(photo2_path)
        print(summary)
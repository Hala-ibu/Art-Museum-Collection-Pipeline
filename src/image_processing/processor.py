import os
import logging
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

logger = logging.getLogger(__name__)

def inspect_image(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f'Image not found: {path}')
    img = Image.open(path)
    width, height = img.size
    file_size = path.stat().st_size
    return {
        'filename': path.name,
        'format': img.format,
        'mode': img.mode,
        'width': width,
        'height': height,
        'aspect_ratio': round(width / height, 3),
        'file_size_bytes': file_size,
        'file_size_kb': round(file_size / 1024, 1),
    }

def resize_artwork(path, output_path, width=800, height=600):
    img = Image.open(path)
    resized = img.resize((width, height), Image.Resampling.LANCZOS)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    resized.save(output_path)
    logger.info(f'Artwork resized: {path.name} -> {width}x{height}')
    return str(output_path)

def generate_thumbnail(path, output_path, size=(200, 200), method='fit'):
    img = Image.open(path).convert('RGB')
    if method == 'fit':
        result = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
    else:
        result = img.copy()
        result.thumbnail(size, Image.Resampling.LANCZOS)
        
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)
    logger.info(f'Thumbnail generated for {path.name}')
    return str(output_path)

def crop_banner(path, output_path):
    img = Image.open(path)
    width, height = img.size
    box = (0, 0, width, height // 3)
    cropped = img.crop(box)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cropped.save(output_path)
    logger.info(f'Banner crop created: {output_path}')
    return str(output_path)

def crop_center_square(path, output_path):
    img = Image.open(path)
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    upper = (h - side) // 2
    box = (left, upper, left + side, upper + side)
    cropped = img.crop(box)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cropped.save(output_path)
    return str(output_path)

def convert_to_webp(path, output_path, quality=80):
    img = Image.open(path).convert('RGB')  
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'WEBP', quality=quality, optimize=True)
    logger.info(f'Converted {path.name} to WebP')
    return str(output_path)

def convert_to_grayscale(path, output_path):
    img = Image.open(path).convert('L')
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return str(output_path)

def apply_sharpen(path, output_path):
    img = Image.open(path)
    sharpened = img.filter(ImageFilter.SHARPEN)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    sharpened.save(output_path)
    return str(output_path)

def apply_blur(path, output_path, radius=2):
    img = Image.open(path)
    blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    blurred.save(output_path)
    return str(output_path)

def enhance_contrast(path, output_path, factor=1.5):
    img = Image.open(path)
    enhanced = ImageEnhance.Contrast(img).enhance(factor)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    enhanced.save(output_path)
    return str(output_path)

def enhance_brightness(path, output_path, factor=1.2):
    img = Image.open(path)
    enhanced = ImageEnhance.Brightness(img).enhance(factor)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    enhanced.save(output_path)
    return str(output_path)

def apply_artwork_filters(image_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with Image.open(image_path) as img:
        img_filtered = img.filter(ImageFilter.SHARPEN)
        enhancer = ImageEnhance.Contrast(img_filtered)
        img_enhanced = enhancer.enhance(1.2)
        save_path = Path(output_dir) / f"filtered_{os.path.basename(image_path)}"
        img_enhanced.save(save_path)
        return str(save_path)
    
def generate_thumbnail(img_path, output_path, max_size=(128, 128)):
    from PIL import Image
    img = Image.open(img_path)
    img.thumbnail(max_size)
    img.save(output_path)
    return str(output_path)

def resize_proportional(img_path, output_path, max_width=500):
    from PIL import Image
    img = Image.open(img_path)
    w_percent = (max_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    resized = img.resize((max_width, h_size), Image.Resampling.LANCZOS)
    resized.save(output_path)
    return str(output_path)

if __name__ == "__main__":
    sample_img = "data/raw/images/92937.jpg"
    if os.path.exists(sample_img):
        print(inspect_image(sample_img))
        print(resize_artwork(sample_img, "data/processed/resized"))
        print(generate_thumbnail(sample_img, "data/processed/thumbnails"))
        print(crop_banner(sample_img, "data/processed/cropped"))
        print(convert_to_webp(sample_img, "data/processed/webp"))
        print(apply_artwork_filters(sample_img, "data/processed/filtered"))
# Art Museum Collection Pipeline

An automated Python-based pipeline designed to process museum artwork images, extract metadata, and synchronize data across local storage, MongoDB, and Google Drive.

## Features
- **Image Processing**: Batch resizing, thumbnail generation, and WebP conversion using Pillow.
- **Metadata Extraction**: Automated EXIF data retrieval (camera specs, timestamps).
- **Database Integration**: Structured storage of image metadata and cloud URLs in MongoDB.
- **Cloud Synchronization**: Automated upload of processed assets to Google Drive via API.

## Project Structure
- `src/image_processing/batch.py`: Main entry point for the pipeline.
- `src/image_processing/processor.py`: Core image manipulation logic.
- `src/storage/mongo.py`: MongoDB connection and record building.
- `src/utils/upload_utils.py`: Google Drive API integration.
- `data/raw/`: Input directory for original images.
- `data/processed/`: Output directory for resized, thumbnail, and WebP files.

![Alternate Text](/Screenshot%202026-04-20%20231352.png)

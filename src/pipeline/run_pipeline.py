import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.mongo import (
    get_db, 
    save_to_mongo, 
    save_transcript, 
    process_images_and_save_metadata
)
from audio_processing.loader import load_audio
from audio_processing.processor import trim_audio, apply_fades, export_audio

from audio_processing.transcriber import (
    transcribe_audio, 
    save_transcript_json, 
    save_transcript_txt, 
    save_transcript_srt
)
from video_processing.loader import extract_audio_from_video
from video_processing.frame_extractor import extract_keyframes
from utils.logger import logging

def run_multimedia_stage():
    logging.info('=== Starting Art Museum Multimedia Pipeline ===')
    db = get_db()

    images_dir = Path('data/raw/images')
    if images_dir.exists():
        image_files = [str(f) for f in images_dir.glob('*') if f.suffix.lower() in ('.png', '.jpg', '.jpeg')]
        process_images_and_save_metadata(image_files, movie_id="museum_asset_001")

    for audio_file in Path('data/raw/audio').glob('*.mp3'):
        try:
            logging.info(f'Processing: {audio_file.name}')
            
            audio_data = load_audio(str(audio_file))
            processed = apply_fades(trim_audio(audio_data, 0, min(30000, len(audio_data))))
            
            clip_path = f'data/processed/audio/{audio_file.stem}_clip.mp3'
            export_audio(processed, clip_path)

            result = transcribe_audio(str(audio_file))

            j, t, s = [f'data/processed/transcripts/{audio_file.stem}{ext}' for ext in ['.json', '.txt', '.srt']]
            save_transcript_json(result, j)
            save_transcript_txt(result, t)
            save_transcript_srt(result, s)

            save_transcript(result, str(audio_file), source_type='audio')

        except Exception as e:
            logging.error(f'Audio Error on {audio_file.name}: {e}')

    for video_file in Path('data/raw/video').glob('*.mp4'):
        try:
            logging.info(f'Processing Video: {video_file.name}')

            extract_keyframes(str(video_file), f'data/processed/frames/{video_file.stem}/')

            audio_out = f'data/processed/audio/{video_file.stem}_from_video.mp3'
            extract_audio_from_video(str(video_file), audio_out)

            result = transcribe_audio(audio_out)

            save_transcript(result, str(video_file), source_type='video_extraction')

        except Exception as e:
            logging.error(f'Video Error on {video_file.name}: {e}')

def run_pipeline():
    try:
        run_multimedia_stage()
        logging.info("--- FULL PIPELINE FINISHED SUCCESSFULLY ---")
    except Exception as e:
        logging.critical(f"Pipeline crashed: {e}")

if __name__ == "__main__":
    run_pipeline()
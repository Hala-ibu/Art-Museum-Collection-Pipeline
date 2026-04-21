import logging
from pathlib import Path
from moviepy import VideoFileClip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_video(file_path):
    return VideoFileClip(str(file_path))

def inspect_video(file_path):
    clip = load_video(file_path)
    info = {
        'filename': Path(file_path).name,
        'duration_s': round(clip.duration, 2),
        'fps': clip.fps,
        'resolution': f"{clip.size[0]}x{clip.size[1]}",
        'has_audio': clip.audio is not None
    }
    
    print(f"\n--- Video Properties: {info['filename']} ---")
    for k, v in info.items():
        print(f"{k:<15}: {v}")
    
    clip.close()
    return info

def extract_audio_from_video(video_path, output_audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path)
    video.close()

def extract_audio(video_path, output_path):
    clip = load_video(video_path)
    if clip.audio:
        clip.audio.write_audiofile(output_path)
        logger.info(f"Audio extracted to: {output_path}")
    else:
        logger.warning("No audio found in video.")
    clip.close()

if __name__ == "__main__":
    video_dir = Path("data/raw/video")
    output_dir = Path("data/processed/audio")
    output_dir.mkdir(parents=True, exist_ok=True)

    video_files = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.mkv"))

    for video in video_files:
        try:
            inspect_video(str(video))
            
            audio_out = output_dir / f"{video.stem}_from_video.mp3"
            extract_audio(str(video), str(audio_out))
            
        except Exception as e:
            print(f"Error processing {video.name}: {e}")
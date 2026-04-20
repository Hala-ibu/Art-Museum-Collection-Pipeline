import logging
from pathlib import Path
from moviepy import VideoFileClip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_keyframes(video_path, output_dir, interval=5.0):
    path = Path(video_path)
    save_path = Path(output_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    
    clip = VideoFileClip(str(path))
    saved_files = []
    
    try:
        duration = clip.duration
        t = 0.0
        while t < duration:
            file_name = save_path / f"{path.stem}_{int(t)}s.png"
            clip.save_frame(str(file_name), t=t)
            saved_files.append(str(file_name))
            t += interval
            
        logger.info(f"Extracted {len(saved_files)} frames from {path.name}")
    finally:
        clip.close()
    return saved_files

if __name__ == "__main__":
    video_folder = Path("data/raw/video")
    
    video_files = list(video_folder.glob("*.mp4"))

    if not video_files:
        print("No videos found in data/raw/video")
    else:
        for video in video_files:
            print(f"\n--- Processing Video: {video.name} ---")
            
            frames_output = Path("data/processed/frames") / video.stem
            
            try:
                frames = extract_keyframes(str(video), frames_output, interval=10.0)
                print(f"Success! {len(frames)} keyframes saved to {frames_output}")
                
            except Exception as e:
                print(f"Failed to process {video.name}: {e}")

        print("\nVideo frame extraction complete.")
import logging
from pathlib import Path
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_audio(path):
    return AudioSegment.from_file(path)

def trim_audio(audio, start, end):
    return audio[start:end]

def apply_fades(audio_segment, fade_in=2000, fade_out=2000):
    return audio_segment.fade_in(fade_in).fade_out(fade_out)

def concatenate_audio(clips):
    combined = AudioSegment.empty()
    for clip in clips:
        combined += clip
    return combined

def export_audio(audio, path, fmt='mp3'):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    audio.export(path, format=fmt)
    logger.info(f"Saved: {path}")

if __name__ == "__main__":
    raw_dir = Path("data/raw/audio")
    proc_dir = Path("data/processed/audio")
    
    files = [f for f in raw_dir.iterdir() if f.suffix.lower() in ['.mp3', '.wav', '.flac']]

    for f in files:
        print(f"\nProcessing {f.name}...")
        audio = load_audio(str(f))

        trimmed = trim_audio(audio, 0, 10000)
        export_audio(trimmed, proc_dir / f"{f.stem}_trimmed.mp3")

        combined = concatenate_audio([trimmed, trimmed])
        export_audio(combined, proc_dir / f"{f.stem}_combined.mp3")

        enhanced = (audio + 5).fade_in(2000).fade_out(2000)
        export_audio(enhanced, proc_dir / f"{f.stem}_enhanced.mp3")

        export_audio(audio, proc_dir / f"{f.stem}_converted.wav", fmt='wav')


import json
import logging
from pathlib import Path
from faster_whisper import WhisperModel
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_model = None

def get_model(model_size='base'):
    global _model
    if _model is None:
        _model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _model

def transcribe_audio(audio_path, model_size='base'):
    model = get_model(model_size)
    segments_gen, info = model.transcribe(str(audio_path), beam_size=5)
    
    segments = []
    texts = []
    for seg in segments_gen:
        print(f"[{seg.start:.2f}s -> {seg.end:.2f}s] {seg.text}")
        segments.append({
            'start': round(seg.start, 2),
            'end': round(seg.end, 2),
            'text': seg.text.strip()
        })
        texts.append(seg.text.strip())

    return {
        'source_file': Path(audio_path).name,
        'language': info.language,
        'duration_s': round(info.duration, 2),
        'segments': segments,
        'full_text': " ".join(texts)
    }

def transcribe_long_audio(audio_path, output_dir, model_size='base', chunk_minutes=5.0):
    perm_dir = Path(output_dir)
    perm_dir.mkdir(parents=True, exist_ok=True)
    
    audio = AudioSegment.from_file(audio_path)
    chunk_ms = int(chunk_minutes * 60 * 1000)
    total_ms = len(audio)
    
    all_segments = []
    all_texts = []
    time_offset = 0.0

    for i, start_ms in enumerate(range(0, total_ms, chunk_ms)):
        end_ms = min(start_ms + chunk_ms, total_ms)
        chunk = audio[start_ms:end_ms]
        
        chunk_filename = f"chunk_{i:03d}.wav"
        chunk_path = perm_dir / chunk_filename
        
        print(f"Exporting and processing: {chunk_filename}")
        chunk.export(str(chunk_path), format="wav")
        
        result = transcribe_audio(str(chunk_path), model_size=model_size)
        
        for seg in result['segments']:
            seg['start'] += time_offset
            seg['end'] += time_offset
            all_segments.append(seg)
            all_texts.append(seg['text'])
        
        time_offset += (end_ms - start_ms) / 1000.0

    final_combined = {'segments': all_segments, 'full_text': " ".join(all_texts)}
    
    save_transcript_json(final_combined, perm_dir / "combined_long_transcript.json")

    return final_combined

def save_transcript_json(result, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

def save_transcript_txt(result, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result.get('full_text', ''))

def save_transcript_srt(result, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(result.get('segments', []), 1):
            start = format_srt_time(seg['start'])
            end = format_srt_time(seg['end'])
            f.write(f"{i}\n{start} --> {end}\n{seg['text']}\n\n")

def format_srt_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int((seconds % 1) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"

if __name__ == "__main__":
    SHORT_AUDIO = 'data/processed/audio/Inception _ The Dream Sequence _ HBO Max_trimmed.mp3'
    
    if Path(SHORT_AUDIO).exists():
        print("\n--- Short Audio Test ---")
        res = transcribe_audio(SHORT_AUDIO)
        output_file = f"data/processed/transcripts/{Path(SHORT_AUDIO).stem}.json"
        save_transcript_json(res, output_file)

    LONG_AUDIO = 'data/raw/audio/Interstellar - Christopher Nolan - Official Warner Bros..mp3'
    if Path(LONG_AUDIO).exists():
        print("\n--- Long Audio Test ---")
        result = transcribe_long_audio(
            audio_path=LONG_AUDIO,
            output_dir='data/processed/transcripts/chunks/',
            model_size='base',
            chunk_minutes=5.0
        )
        print(f"Total segments: {len(result['segments'])}")
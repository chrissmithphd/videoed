# Background Music Research - B-roll Video Reels

**Date:** 2026-06-24  
**Purpose:** Add calm background music to extracted video reels

---

## Free Music Sources (Legal & Automated)

### Recommended Platforms

1. **Incompetech (incompetech.com)**
   - License: CC-BY 4.0 (requires attribution)
   - Extensive ambient/background catalog
   - Attribution: "Music by Kevin MacLeod (incompetech.com)"
   - Download: Direct MP3/OGG links
   - Best for: Automated selection, consistent quality

2. **Bensound (bensound.com)**
   - License: Perpetual for social media/YouTube
   - Calm/ambient categories
   - No API but direct downloads
   - Best for: Hand-picked professional tracks

3. **Pixabay Music (pixabay.com/music)**
   - License: Royalty-free, no attribution required
   - API available (requires auth)
   - Large catalog with search/filters
   - Best for: Programmatic access

4. **ccMixter (ccmixter.org)**
   - License: Various CC licenses
   - Searchable by BPM/style/instrument
   - RSS feeds available for automation
   - Best for: Diverse styles, BPM matching

5. **Free Music Archive (freemusicarchive.org)**
   - License: Various CC licenses (check per track)
   - High-quality curated content
   - API available
   - Best for: Professional-grade tracks

---

## Audio Characteristics for B-roll

### Optimal Specifications

**Genres:**
- Ambient
- Lo-fi instrumental
- Acoustic instrumental
- Cinematic atmosphere
- Minimal electronic

**Tempo:**
- **BPM:** 60-90 (slower = calmer)
- Avoid fast tempos (>120 BPM) for B-roll

**Technical Specs:**
- **Bitrate:** 128kbps MP3 minimum, 320kbps or WAV for professional
- **Sample Rate:** 44.1kHz or 48kHz
- **Format:** MP3, WAV, OGG

**Volume Mixing:**
- Background music: -10dB to -20dB below main audio
- In code: 30-50% volume (`with_volume_scaled(0.3)`)
- Always normalize before mixing

---

## Python Libraries

### MoviePy (v2.2.1) - RECOMMENDED

**Best for:** Video + audio compositing

**Installation:**
```bash
pip install moviepy
```

**Capabilities:**
- Volume control
- Fade in/out
- Loop/trim audio to match video length
- Audio compositing (mix multiple tracks)

**Example - Basic Overlay:**
```python
from moviepy import VideoFileClip, AudioFileClip

video = VideoFileClip("reel.mp4")
music = AudioFileClip("background.mp3")

# Match duration, reduce volume, add fades
music = (music
    .with_duration(video.duration)
    .with_volume_scaled(0.3)
    .audio_fadein(2)
    .audio_fadeout(2))

# Apply to video
final = video.with_audio(music)
final.write_videofile("reel_with_music.mp4", codec='libx264', audio_codec='aac')
```

**Example - Mix Original + Background:**
```python
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip

video = VideoFileClip("reel.mp4")
music = AudioFileClip("background.mp3")

# Prepare background music
music = (music
    .with_duration(video.duration)
    .with_volume_scaled(0.3)
    .audio_fadein(2)
    .audio_fadeout(2))

# Mix original video audio with background
if video.audio:
    mixed_audio = CompositeAudioClip([video.audio, music])
else:
    mixed_audio = music

final = video.with_audio(mixed_audio)
final.write_videofile("output.mp4")
```

---

### Pydub (v0.25.1) - RECOMMENDED for Audio Preprocessing

**Best for:** Audio manipulation before adding to video

**Installation:**
```bash
pip install pydub
```

**Capabilities:**
- Normalize audio levels
- Loop audio
- Trim/split audio
- Fade in/out
- Volume adjustment
- Format conversion

**Example - Prepare Audio:**
```python
from pydub import AudioSegment

# Load audio
audio = AudioSegment.from_file("music.mp3")

# Normalize levels (prevent clipping)
audio = audio.normalize()

# Loop 3 times and trim to 60 seconds
audio = (audio * 3)[:60000]  # milliseconds

# Fade in/out and reduce volume by 10dB
audio = audio.fade_in(2000).fade_out(2000) - 10

# Export
audio.export("prepared.mp3", format="mp3", bitrate="192k")
```

**Example - Advanced Processing:**
```python
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

audio = AudioSegment.from_file("music.mp3")

# Normalize and compress dynamic range (smoother for background)
audio = normalize(audio)
audio = compress_dynamic_range(audio, threshold=-20, ratio=4.0)

# Set to specific duration with loop
target_duration_ms = 25000  # 25 seconds
if len(audio) < target_duration_ms:
    # Loop to reach duration
    loops_needed = (target_duration_ms // len(audio)) + 1
    audio = (audio * loops_needed)[:target_duration_ms]
else:
    # Trim if too long
    audio = audio[:target_duration_ms]

audio.export("processed.mp3", format="mp3")
```

---

### ffmpeg-python (v0.2.0) - Lower-Level Alternative

**Use only if MoviePy insufficient**

**Example:**
```python
import ffmpeg

(
    ffmpeg
    .input('video.mp4')
    .input('music.mp3')
    .filter('amerge')
    .output('output.mp4', acodec='aac', vcodec='copy')
    .run()
)
```

---

## Automation Strategy

### Random Music Selection

```python
import random
import os
from pathlib import Path

def select_random_music(music_dir: str, mood: str = None) -> str:
    """
    Select random music track from directory.
    Optional mood filtering if files organized by subdirectory.
    """
    music_path = Path(music_dir)
    
    if mood:
        music_path = music_path / mood
    
    tracks = list(music_path.glob('*.mp3')) + list(music_path.glob('*.wav'))
    
    if not tracks:
        raise FileNotFoundError(f"No music files found in {music_path}")
    
    return str(random.choice(tracks))

# Usage
music_file = select_random_music('music/calm/')
```

---

### Complete Automation Pipeline

```python
from pathlib import Path
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from pydub import AudioSegment
import random
import os

def add_background_music(video_path: str, 
                        music_dir: str,
                        output_path: str,
                        volume: float = 0.3,
                        fade_duration: float = 2.0,
                        normalize: bool = True):
    """
    Add random background music to video with automatic processing.
    
    Args:
        video_path: Path to input video
        music_dir: Directory containing music files
        output_path: Path for output video
        volume: Background music volume (0.0-1.0)
        fade_duration: Fade in/out duration in seconds
        normalize: Whether to normalize audio levels
    """
    # Select random music
    music_files = list(Path(music_dir).glob('*.mp3'))
    if not music_files:
        raise FileNotFoundError(f"No music files in {music_dir}")
    
    music_path = random.choice(music_files)
    print(f"Selected music: {music_path.name}")
    
    # Load video
    video = VideoFileClip(video_path)
    video_duration = video.duration
    
    # Preprocess audio with Pydub (optional but recommended)
    if normalize:
        audio_segment = AudioSegment.from_file(str(music_path))
        audio_segment = audio_segment.normalize()
        
        # Loop or trim to match video duration
        target_ms = int(video_duration * 1000)
        if len(audio_segment) < target_ms:
            loops = (target_ms // len(audio_segment)) + 1
            audio_segment = (audio_segment * loops)[:target_ms]
        else:
            audio_segment = audio_segment[:target_ms]
        
        # Export temporary file
        temp_music = "/tmp/processed_music.mp3"
        audio_segment.export(temp_music, format="mp3")
        music_path = temp_music
    
    # Load processed music
    music = AudioFileClip(str(music_path))
    
    # Apply volume and fades
    music = (music
        .with_duration(video_duration)
        .with_volume_scaled(volume)
        .audio_fadein(fade_duration)
        .audio_fadeout(fade_duration))
    
    # Mix with original audio if present
    if video.audio:
        final_audio = CompositeAudioClip([video.audio, music])
    else:
        final_audio = music
    
    # Create final video
    final = video.with_audio(final_audio)
    
    # Write output
    final.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        audio_bitrate='192k',
        preset='medium',
        ffmpeg_params=['-crf', '18']  # High quality
    )
    
    # Cleanup
    video.close()
    music.close()
    if normalize and os.path.exists(temp_music):
        os.remove(temp_music)
    
    print(f"✓ Created: {output_path}")

# Usage
add_background_music(
    video_path='reel_01.mp4',
    music_dir='music/calm/',
    output_path='reel_01_with_music.mp4',
    volume=0.35,
    fade_duration=2.0,
    normalize=True
)
```

---

## Best Practices

### Volume Mixing
- **Background only:** 30-40% volume (`0.3-0.4`)
- **With voiceover:** 20-30% volume (`0.2-0.3`)
- **With ambient sounds:** 35-50% volume (`0.35-0.5`)

### Audio Normalization
- Always normalize music before mixing
- Prevents clipping and distortion
- Use Pydub's `normalize()` function

### Fade In/Out
- Minimum: 1 second
- Recommended: 2-3 seconds for smooth transitions
- Matches typical B-roll reel duration

### Music Organization
```
music/
├── calm/
│   ├── ambient_01.mp3
│   ├── ambient_02.mp3
│   └── ...
├── upbeat/
│   └── ...
└── cinematic/
    └── ...
```

### BPM Matching (Advanced)
```python
# Use librosa for BPM detection
import librosa

y, sr = librosa.load('music.mp3')
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
print(f"BPM: {tempo:.0f}")

# Filter music by BPM range for B-roll (60-90)
if 60 <= tempo <= 90:
    # Use this track
    pass
```

---

## Installation Commands

### Minimal (MoviePy only)
```bash
pip install moviepy
```

### Full (with preprocessing)
```bash
pip install moviepy pydub
```

### With audio analysis
```bash
pip install moviepy pydub librosa
```

---

## License Considerations

### Creative Commons Licenses

**CC0 (Public Domain):**
- Use freely, no attribution required
- Best for automation

**CC-BY (Attribution):**
- Must credit artist
- Add attribution in video description
- Format: "Music by [Artist] ([Source URL])"

**CC-BY-SA (Attribution + ShareAlike):**
- Must credit artist
- Derivative works must use same license
- Check compatibility with your use case

**CC-BY-NC (Attribution + NonCommercial):**
- Cannot use for commercial purposes
- OK for personal/educational projects

### Royalty-Free vs. Copyright-Free
- **Royalty-free:** Pay once (or free), use multiple times, still copyrighted
- **Copyright-free (CC0):** True public domain, no restrictions

---

## Example Music Sources

### Calm/Ambient Tracks (Incompetech)
- "Meditation Impromptu 01" - Very calm, minimal
- "Flowing Rocks" - Gentle ambient
- "Atlantean Twilight" - Atmospheric
- "Dreamlike" - Soft piano

### Search Terms
- "calm background music"
- "ambient instrumental"
- "peaceful background"
- "lo-fi study music" (without vocals)
- "cinematic ambient"

---

**Next Steps:**
1. Download 5-10 calm tracks to `music/calm/` directory
2. Test automation script with sample video
3. Adjust volume/fade parameters based on results
4. Integrate into main reel extraction pipeline

---

*Research completed: 2026-06-24*

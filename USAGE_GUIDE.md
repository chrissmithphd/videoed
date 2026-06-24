# VideoReel Generator - Usage Guide

**Quick guide for extracting interesting reels from B-roll footage**

---

## Quick Start

### 1. Basic Extraction (No Music)

Extract 5 best reels from a video:

```bash
source venv/bin/activate
python extract_reels.py your_video.mp4
```

Output: `reels/your_video_reel_01.mp4`, `reels/your_video_reel_02.mp4`, etc.

### 2. Extract More Reels

Get 10 reels instead of 5:

```bash
python extract_reels.py your_video.mp4 -n 10
```

### 3. Process Multiple Videos

Process all videos in current directory:

```bash
python extract_reels.py *.mp4 -n 5
```

### 4. With Background Music

First, create a music directory and add some calm MP3 files:

```bash
mkdir music/calm
# Add your music files to music/calm/
```

Then extract with music overlay:

```bash
python extract_reels_with_music.py your_video.mp4 \
    --add-music \
    --music-dir music/calm/ \
    --music-volume 0.35
```

---

## Command Reference

### Basic Script: `extract_reels.py`

```bash
python extract_reels.py [OPTIONS] VIDEO [VIDEO ...]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `-o, --output DIR` | `reels/` | Output directory |
| `-n, --num-reels N` | `5` | Number of reels per video |
| `--min-duration N` | `10` | Minimum reel duration (seconds) |
| `--max-duration N` | `30` | Maximum reel duration (seconds) |
| `--target-duration N` | `20` | Target reel duration (seconds) |
| `--sample-rate N` | `5` | Process every Nth frame (higher = faster) |
| `--save-analysis` | off | Save JSON analysis file |

**Examples:**

```bash
# Extract 3 short reels (10-15 seconds each)
python extract_reels.py video.mp4 -n 3 --min-duration 10 --max-duration 15

# Fast processing (process every 10th frame)
python extract_reels.py video.mp4 --sample-rate 10

# Save analysis data
python extract_reels.py video.mp4 --save-analysis
```

---

### Music Script: `extract_reels_with_music.py`

```bash
python extract_reels_with_music.py [OPTIONS] VIDEO [VIDEO ...]
```

**Additional Music Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--add-music` | off | Enable music overlay |
| `--music-dir DIR` | required | Directory with music files |
| `--music-volume N` | `0.35` | Music volume (0.0-1.0) |
| `--music-fade N` | `2.0` | Fade in/out duration (seconds) |

**Examples:**

```bash
# Basic with music
python extract_reels_with_music.py video.mp4 \
    --add-music \
    --music-dir music/calm/

# Quieter background music
python extract_reels_with_music.py video.mp4 \
    --add-music \
    --music-dir music/calm/ \
    --music-volume 0.2

# Longer fades (smoother)
python extract_reels_with_music.py video.mp4 \
    --add-music \
    --music-dir music/calm/ \
    --music-fade 3.0
```

---

## Understanding B-roll Scoring

The tool scores segments based on these factors:

### Scoring Weights (B-roll optimized)

- **Motion (25%):** Gentle, smooth motion preferred
  - Too static = boring
  - Too fast = chaotic
  - Ideal: 2-8 pixels/frame of motion

- **Visual Complexity (35%):** Edge density, scene detail
  - Higher weight for B-roll
  - Richer scenes score higher

- **Stability (25%):** Penalizes shaky footage
  - Important for professional B-roll
  - Smooth camera movement preferred

- **Color Richness (15%):** Saturation and variance
  - Vibrant, varied colors score higher

### What Makes a "Good" B-roll Segment?

✅ **High Scoring:**
- Slow camera pans across detailed scenes
- Gentle motion with stable camera
- Rich colors and visual interest
- Natural scene transitions

❌ **Low Scoring:**
- Static, unchanging frames
- Shaky handheld footage
- Fast, chaotic movement
- Low visual complexity (blank walls, etc.)

---

## Performance Optimization

### Sample Rate Tuning

The `--sample-rate` parameter controls how many frames to analyze:

| Sample Rate | Processing Speed | Accuracy |
|-------------|------------------|----------|
| `1` | Very slow (all frames) | Best |
| `5` | Moderate (default) | Good |
| `10` | Fast | Acceptable |
| `15+` | Very fast | May miss details |

**Recommendation:**
- **First pass:** Use `--sample-rate 10` for quick preview
- **Final extraction:** Use `--sample-rate 5` for better accuracy

### Expected Processing Times

**Test case: 140-second 1080p video @ 30fps**

| Sample Rate | Processing Time | Output Quality |
|-------------|----------------|----------------|
| 5 | ~5-7 minutes | Good |
| 10 | ~3-4 minutes | Acceptable |
| 15 | ~2-3 minutes | Lower accuracy |

**With music overlay:** Add ~30 seconds per reel for music processing.

---

## Output Files

### Directory Structure

```
reels/
├── video1_reel_01_score0.78.mp4
├── video1_reel_02_score0.74.mp4
├── video1_reel_03_score0.71.mp4
├── video1_analysis.json           (if --save-analysis)
├── video2_reel_01_score0.82.mp4
└── ...
```

### File Naming

Format: `{video_name}_reel_{number}_score{score}.mp4`

- **video_name:** Original filename (without extension)
- **number:** 01, 02, 03... (ranked by score)
- **score:** Interest score (0.0-1.0, higher = better)

### Analysis JSON (Optional)

With `--save-analysis`, creates:

```json
{
  "video_info": {
    "duration": 140.5,
    "fps": 30.0,
    "width": 1920,
    "height": 1080,
    "codec": "h264"
  },
  "segments": [
    {
      "start_time": 45.2,
      "end_time": 65.2,
      "duration": 20.0,
      "score": 0.782,
      "frame_start": 1356,
      "frame_end": 1956
    },
    ...
  ]
}
```

---

## Music Setup

### Downloading Free Music

#### Option 1: Incompetech (CC-BY)

1. Visit: https://incompetech.com/music/royalty-free/music.html
2. Search for "calm" or "ambient"
3. Download MP3 files
4. Add attribution in video description: "Music by Kevin MacLeod (incompetech.com)"

**Recommended tracks:**
- Meditation Impromptu 01
- Flowing Rocks
- Atlantean Twilight

#### Option 2: Pixabay Music

1. Visit: https://pixabay.com/music/search/calm/
2. Filter by "Calm" or "Ambient"
3. Download (no attribution required)
4. Save to `music/calm/`

#### Option 3: Bensound

1. Visit: https://www.bensound.com
2. Browse "Acoustic/Folk" or "Ambient" categories
3. Download (perpetual license for social media)

### Music Directory Structure

```
music/
├── calm/
│   ├── ambient_01.mp3
│   ├── ambient_02.mp3
│   ├── flowing_rocks.mp3
│   └── meditation.mp3
├── upbeat/     (for future use)
└── cinematic/  (for future use)
```

### Music Volume Guidelines

| Use Case | Recommended Volume |
|----------|--------------------|
| Background only (no voice) | `0.35-0.40` |
| With voiceover (future) | `0.20-0.30` |
| Ambient sounds present | `0.35-0.50` |

---

## Troubleshooting

### Issue: "No suitable segments found"

**Causes:**
- Video too short (< min_duration)
- Video too static (low motion/complexity)
- Thresholds too strict

**Solutions:**
```bash
# Lower minimum duration
python extract_reels.py video.mp4 --min-duration 5

# Accept more segments
python extract_reels.py video.mp4 -n 10

# Use faster sample rate (process more frames)
python extract_reels.py video.mp4 --sample-rate 3
```

### Issue: Extracted segments are boring

**Solutions:**
1. Increase `--num-reels` to get more candidates
2. Lower `--sample-rate` for better analysis
3. Check that video has motion/activity
4. B-roll scoring favors smooth motion, not action

### Issue: "MoviePy not installed"

**Solution:**
```bash
source venv/bin/activate
pip install moviepy pydub
```

### Issue: Processing is very slow

**Solutions:**
1. Increase `--sample-rate` (process fewer frames)
2. Use smaller videos for testing first
3. Optical flow is CPU-intensive (expected ~1x realtime)

### Issue: Music overlay fails

**Causes:**
- MoviePy not installed
- Music directory not found
- Music files not MP3/WAV

**Solutions:**
```bash
# Install MoviePy
pip install moviepy

# Check music directory
ls music/calm/*.mp3

# Convert files if needed (requires ffmpeg)
ffmpeg -i music.m4a -acodec mp3 music.mp3
```

---

## Advanced Usage

### Batch Processing Script

```bash
#!/bin/bash
# process_all.sh

for video in *.mp4; do
    echo "Processing $video..."
    python extract_reels.py "$video" \
        -n 5 \
        --sample-rate 10 \
        -o "reels_$(basename "$video" .mp4)"
done
```

### Custom Scoring Weights

To modify scoring weights, edit `extract_reels.py`:

```python
# Line ~35 - BRollAnalyzer __init__
self.analyzer = BRollAnalyzer(
    motion_weight=0.25,      # Adjust these
    complexity_weight=0.35,
    stability_weight=0.25,
    color_weight=0.15
)
```

For action footage (not B-roll):
```python
motion_weight=0.5,       # Higher motion weight
complexity_weight=0.2,
stability_weight=0.1,    # Lower stability (shaky OK)
color_weight=0.2
```

---

## Tips & Best Practices

### For Best Results

1. **Video Quality:** Use 1080p or higher source videos
2. **Minimum Length:** Videos should be at least 2-3x longer than target reel duration
3. **Content Variety:** Videos with varied scenes produce better reels
4. **Camera Movement:** Gentle pans/tracking shots score well
5. **Lighting:** Well-lit, colorful scenes score higher

### Workflow Recommendations

**1. Quick Preview (find how many reels possible):**
```bash
python extract_reels.py video.mp4 -n 20 --sample-rate 15 --save-analysis
# Review analysis.json to see scores
```

**2. Extract Top Reels (high quality):**
```bash
python extract_reels.py video.mp4 -n 5 --sample-rate 5
```

**3. Add Music (final output):**
```bash
python extract_reels_with_music.py video.mp4 \
    -n 5 \
    --sample-rate 5 \
    --add-music \
    --music-dir music/calm/ \
    --music-volume 0.35
```

### Storage Considerations

- **Input:** 336MB video (2.4 minutes)
- **Output:** ~5-10MB per 20-second reel
- **Total:** For 5 reels = ~25-50MB

Allow ~15-20% of input size for output storage.

---

## Next Steps

### Current Capabilities ✅
- Extract interesting segments from B-roll
- Score based on motion, complexity, stability, color
- Add background music with automatic mixing
- Batch processing

### Future Enhancements (Planned)
- Text overlay / captions
- Automatic speech-to-text
- Video transitions
- Color grading
- Face/person detection weighting
- Web interface

---

## Getting Help

### Documentation
- **RESEARCH.md** - Technical details and library analysis
- **MUSIC_RESEARCH.md** - Music sources and overlay techniques
- **README.md** - Project overview

### Common Issues
See "Troubleshooting" section above

### Example Videos
Test with sample videos first (5-10 minutes recommended)

---

*Last updated: 2026-06-24*

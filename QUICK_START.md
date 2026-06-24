# Quick Start Guide - VideoReel Generator

**Get started in 5 minutes**

---

## What This Does

Automatically extracts interesting 10-30 second segments from your B-roll footage based on:
- Motion (gentle pans preferred)
- Visual complexity
- Camera stability
- Color richness

---

## Installation

```bash
# 1. Activate virtual environment (already created)
source venv/bin/activate

# 2. Dependencies are already installed:
# - opencv-python, scenedetect, av, numpy, tqdm
# - For music: pip install moviepy pydub (optional)
```

---

## Basic Usage

### Extract 5 Best Reels

```bash
python extract_reels.py your_video.mp4
```

Output: `reels/your_video_reel_01.mp4` ... `reel_05.mp4`

### Extract More Reels

```bash
python extract_reels.py your_video.mp4 -n 10
```

### Process Multiple Videos

```bash
python extract_reels.py *.mp4
```

---

## With Background Music

### 1. Set Up Music

```bash
mkdir -p music/calm
# Add MP3 files to music/calm/
```

**Free music sources:**
- [Pixabay Music](https://pixabay.com/music/) (no attribution)
- [Incompetech](https://incompetech.com/music/) (requires attribution)
- [Bensound](https://bensound.com) (perpetual license)

### 2. Install Music Libraries

```bash
pip install moviepy pydub
```

### 3. Extract with Music

```bash
python extract_reels_with_music.py your_video.mp4 \
    --add-music \
    --music-dir music/calm/
```

---

## Current Test Status

**Two videos are currently being processed:**

1. `PXL_20260624_160111402.mp4` (336MB, 140s)
   - Extracting 3 reels
   - Status: ~50-60% complete

2. `PXL_20260624_160346844.mp4` (163MB, 68s)
   - Extracting 2 reels  
   - Status: ~42% complete

**Check results:**
```bash
ls -lh reels/
ls -lh reels_test/
```

---

## Common Options

```bash
# Faster processing (lower quality analysis)
python extract_reels.py video.mp4 --sample-rate 15

# More accurate (slower)
python extract_reels.py video.mp4 --sample-rate 3

# Shorter reels
python extract_reels.py video.mp4 --max-duration 15

# Save analysis data
python extract_reels.py video.mp4 --save-analysis
```

---

## Expected Processing Time

- **Sample rate 10:** ~3-5 minutes per minute of video
- **Sample rate 5:** ~5-10 minutes per minute of video

Your 140-second video = ~5-7 minutes processing time

---

## Troubleshooting

### No reels extracted?

```bash
# Lower minimum duration
python extract_reels.py video.mp4 --min-duration 5

# Extract more candidates
python extract_reels.py video.mp4 -n 15
```

### Too slow?

```bash
# Process fewer frames
python extract_reels.py video.mp4 --sample-rate 15
```

### Music not working?

```bash
# Install libraries
pip install moviepy pydub

# Check music directory
ls music/calm/*.mp3
```

---

## Next Steps

1. **Wait for processing to complete** (~5 minutes remaining)
2. **Review extracted reels** in `reels/` directory
3. **Test music overlay** on one reel
4. **Adjust parameters** if needed

---

## Full Documentation

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Complete user guide
- **[MUSIC_RESEARCH.md](MUSIC_RESEARCH.md)** - Music sources and setup
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical details
- **[README.md](README.md)** - Project overview

---

**Questions?** Check USAGE_GUIDE.md for examples and troubleshooting.

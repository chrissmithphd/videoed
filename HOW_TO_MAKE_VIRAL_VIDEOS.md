# How to Make Viral Videos - Complete Guide

**Last Updated:** 2026-06-24  
**Status:** ✅ TESTED & WORKING

---

## Quick Start (3 Steps)

```bash
# 1. Extract interesting 20-second segments with music
python3 extract_reels_with_music.py your_video.mp4 -n 5 -o reels/

# 2. Add text overlay from TextThoughts.txt
python3 add_text_simple.py reels/*.mp4 test_outputs/final.mp4

# 3. Done! Check test_outputs/final.mp4
```

---

## What You Get

✅ **20-second viral-style reels** with:
- Automatically selected "interesting" segments (motion + complexity scoring)
- Professional background music (Kevin MacLeod tracks)
- 90° rotation correction (portrait phone videos → upright)
- Bold text overlay (3 lines from TextThoughts.txt)
- White text with black outline, large font (80pt)

---

## Complete Pipeline

```
Your Video (30min-2hr)
    ↓
[Analysis: Find interesting segments - ~5-10 min per video]
    ↓
[Extract with Music: 20s clips - ~2-3 min per clip]
    ↓
[Add Text Overlay: From TextThoughts.txt - ~30s per clip]
    ↓
Final Viral Reels ✓
```

---

## Step-by-Step Instructions

### 1. Prepare Your Video

Put your phone video in the project directory:
```bash
cd /home/cbsmith/git/videoed
# Copy your video here (e.g., my_broll.mp4)
```

### 2. Extract Reels with Music

```bash
python3 extract_reels_with_music.py my_broll.mp4 -n 5 -o reels/
```

**What this does:**
- Analyzes entire video for motion, visual complexity, color
- Finds top 5 most "interesting" 20-second segments
- Rotates portrait videos to upright
- Adds random professional music from `music/viral/`
- Outputs to `reels/` directory

**Options:**
```bash
-n 5                    # Number of reels to extract (default: 5)
--target-duration 20    # Length of each reel (default: 20s)
--music-volume 0.4      # Music volume 0-1 (default: 0.3)
-o reels/              # Output directory
```

**Time:** ~5-10 minutes for 30-60 minute video

### 3. Add Text Overlay

```bash
python3 add_text_simple.py reels/my_broll_reel_01_score0.53.mp4 test_outputs/final_reel.mp4
```

**What this does:**
- Reads first segment from `TextThoughts.txt`
- Takes first 3 lines
- Removes apostrophes (FFmpeg compatibility)
- Splits text evenly across video duration
- 80pt white bold text with 5px black outline, centered

**Time:** ~30 seconds per reel

### 4. View Your Reels

```bash
ffplay test_outputs/final_reel.mp4
# or open in your video player
```

---

## Files & Directories

### Input Files
- **Your video**: Any MP4 from phone (portrait or landscape)
- **TextThoughts.txt**: Text content (segments separated by `--`)

### Music Library
- `music/viral/Happy_Alley.mp3` - Upbeat rock (Kevin MacLeod)
- `music/viral/Funky_One.mp3` - Groovy funk (Kevin MacLeod)
- `music/viral/Go_Cart.mp3` - Energetic electronic (Kevin MacLeod)
- `music/viral/sneaky_snitch.mp3` - Playful (Kevin MacLeod)

**License:** CC-BY 4.0 - Add to video description:
```
Music by Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0
```

### Output Directories
- **reels/**: Extracted segments with music (no text yet)
- **test_outputs/**: Final reels with text overlay

---

## Working Scripts (Tested)

✅ **extract_reels_with_music.py** - Main extraction with music  
✅ **add_text_simple.py** - Add text overlay (simple, works)  
✅ **extract_reels.py** - Modular analysis only (outputs JSON)

❌ **add_text_overlay.py** - Complex version (has bugs, don't use)

---

## TextThoughts.txt Format

```
Most kids aren't addicted to screens.
They're addicted to easy.
Code Ninjas isnt easy.

--

Kids don't build confidence by being told they're amazing.
They build confidence by doing something they thought they couldn't do.
That's every day at Code Ninjas.

--

[More segments...]
```

**Format Rules:**
- Segments separated by `--` on its own line
- Script takes first 3 lines of first segment
- Apostrophes automatically removed for FFmpeg compatibility

---

## Tested Example

**Input:**
- Video: `PXL_20260624_160111402.mp4` (140 seconds, portrait phone video)
- Text: First segment from TextThoughts.txt

**Output:**
- `test_outputs/final_with_text.mp4` (20 seconds)
- Features:
  - Segment extracted from 115.2s-134.8s (highest interest score: 0.53)
  - Music: "Funky One" by Kevin MacLeod
  - Rotation: 90° counter-clockwise applied (portrait → upright)
  - Text: 3 lines, 6.7s each
  - Size: 11 MB

**Status:** ✅ TESTED & WORKING

---

## Troubleshooting

### Video is sideways
- Script auto-detects and corrects 90° rotation
- If still wrong, video may have unusual rotation tag

### No music
- Check `music/viral/` has MP3 files
- Download more: `python3 download_incompetech.py`

### Text not showing
- Check TextThoughts.txt exists
- Verify first segment has at least 3 lines
- Apostrophes are automatically removed

### "No interesting segments found"
- Video may be too static (no motion)
- Try lower `--min-duration` (default 10s)
- Check video isn't corrupted

---

## Advanced Usage

### Batch Process Multiple Videos

```bash
# Extract reels from all MP4 files
for video in *.mp4; do
    python3 extract_reels_with_music.py "$video" -n 3 -o reels/
done

# Add text to all reels
for reel in reels/*.mp4; do
    output="test_outputs/$(basename "$reel" .mp4)_final.mp4"
    python3 add_text_simple.py "$reel" "$output"
done
```

### Use Different Music

Edit `music/viral/` directory - script randomly picks from available files.

### Adjust Text Timing

Edit `add_text_simple.py` line 23:
```python
time_per_line = duration / len(text_lines)  # Currently even split
```

### Use Different Text Segment

Edit `add_text_simple.py` line 18:
```python
return segments[0].split('\n')  # Change [0] to [1], [2], etc.
```

---

## System Requirements

- **Python 3.10+** with venv
- **FFmpeg 6.1+** (for audio and text overlay)
- **Dependencies:**
  - PyAV (video I/O)
  - OpenCV (motion analysis)
  - NumPy, SciPy (analysis)
  - tqdm (progress bars)

**Install:**
```bash
source venv/bin/activate
pip install av opencv-python numpy scipy tqdm
```

---

## Performance

**140-second input video:**
- Analysis: ~8 minutes (optical flow on every 5th frame)
- Extraction: ~2-3 minutes per reel
- Text overlay: ~30 seconds per reel

**Total:** ~15 minutes for 5 complete reels

---

## What's Next

- ✅ Extract segments ✓
- ✅ Add music ✓
- ✅ Add text overlay ✓
- ⏭️ Batch processing script
- ⏭️ Different text styles (top/bottom, animated)
- ⏭️ Custom fonts
- ⏭️ Audio offset (skip music intros)

---

## Support Files

- **RESEARCH.md** - Technical details on video analysis
- **MUSIC_GENERATION_RESEARCH.md** - Music synthesis (alternative to downloads)
- **TEXT_OVERLAY_RESEARCH.md** - Text overlay methods comparison

---

**Questions? Check test_outputs/ for working examples.**

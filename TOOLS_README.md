# VideoReel Generator - Modular Tools

**Created:** 2026-06-25  
**Status:** Ready to use

## Overview

This project provides 4 modular command-line tools for creating viral social media reels from long videos:

1. **`extract_segments.py`** - Find and extract interesting clips
2. **`replace_audio.py`** - Replace audio with viral music  
3. **`add_text_overlay.py`** - Add text overlays
4. **`make_viral_reels.sh`** - Run all 3 tools in sequence (convenience script)

Each tool does **ONE thing** and can be used independently or chained together.

---

## Quick Start

### Setup (First Time Only)

```bash
# Create virtual environment and install dependencies
python3 -m venv .venv
.venv/bin/pip install av opencv-python numpy tqdm

# Make sure you have music files
ls music/viral/  # Should show *.mp3 files
```

### Create Viral Reels (One Command)

```bash
./make_viral_reels.sh my_video.mp4
# Output: final_reels/my_video_segment_01.mp4, etc.
```

---

## Tool 1: Extract Segments

**Purpose:** Find and extract interesting 10-30 second clips from long videos.

**What it does:**
- Analyzes video for motion, visual complexity, and color
- Scores each potential segment
- Extracts top N segments to separate files
- **Preserves original orientation** (no rotation)
- **Preserves original audio** (no modifications)

**Usage:**

```bash
.venv/bin/python3 extract_segments.py input.mp4 --output-dir segments/ -n 5
```

**Arguments:**
- `input` - Input video file (required)
- `--output-dir` - Where to save extracted segments (required)
- `-n, --num-segments` - Number of segments to extract (default: 5)
- `--target-duration` - Target segment length in seconds (default: 20)
- `--min-duration` - Minimum segment length (default: 10)
- `--max-duration` - Maximum segment length (default: 30)

**Output:**
- `segments/input_segment_01.mp4`
- `segments/input_segment_02.mp4`
- etc.

**Example:**

```bash
# Extract 3 segments, 15 seconds each
.venv/bin/python3 extract_segments.py video.mp4 --output-dir clips/ -n 3 --target-duration 15
```

---

## Tool 2: Replace Audio

**Purpose:** Replace video audio with random music from a directory.

**What it does:**
- Randomly picks a music file from specified directory
- Replaces audio track
- **No video changes** (same resolution, orientation, quality)
- **Fast** (uses FFmpeg `-c:v copy`, no video re-encoding)

**Usage:**

```bash
.venv/bin/python3 replace_audio.py video1.mp4 video2.mp4 \
    --music-dir music/viral/ --output-dir with_music/
```

**Arguments:**
- `videos` - One or more video files (can use wildcards: `segments/*.mp4`)
- `--music-dir` - Directory containing music files (`.mp3` or `.wav`)
- `--output-dir` - Where to save videos with new audio

**Output:**
- Same filename as input, in output directory
- Same video stream (orientation, resolution, quality)
- New audio stream (from music directory)

**Example:**

```bash
# Replace audio for all segments
.venv/bin/python3 replace_audio.py segments/*.mp4 \
    --music-dir music/viral/ --output-dir with_music/
```

---

## Tool 3: Add Text Overlay

**Purpose:** Add timed text overlay to videos.

**What it does:**
- Reads first segment from `TextThoughts.txt` (before first `--`)
- Splits text into 2-3 word phrases
- Times phrases evenly across video duration
- 80pt white text with black border, centered
- **Preserves audio** (no audio changes)
- **Works on any orientation** (portrait or landscape)

**Usage:**

```bash
.venv/bin/python3 add_text_overlay.py video1.mp4 \
    --text-file TextThoughts.txt --output-dir final/
```

**Arguments:**
- `videos` - One or more video files
- `--text-file` - Text file (uses first segment before `--`)
- `--output-dir` - Where to save videos with text overlay
- `--max-words` - Max words per phrase (default: 3)

**Output:**
- Same filename as input, in output directory
- Same video with text burned in
- Same audio stream (preserved)

**Example:**

```bash
# Add text to all videos with music
.venv/bin/python3 add_text_overlay.py with_music/*.mp4 \
    --text-file TextThoughts.txt --output-dir final/
```

---

## Tool 4: Pipeline Script (All-in-One)

**Purpose:** Run all 3 tools in sequence automatically.

**What it does:**

```bash
# Step 1: Extract segments
extract_segments.py → temp/segments/

# Step 2: Add music
replace_audio.py → temp/with_music/

# Step 3: Add text
add_text_overlay.py → final_reels/

# Cleanup: Remove temp/ directory
```

**Usage:**

```bash
./make_viral_reels.sh video.mp4 [num_segments]
```

**Arguments:**
- `video.mp4` - Input video file
- `num_segments` - Optional, number of reels to create (default: 5)

**Output:**
- `final_reels/video_segment_01.mp4` (with music + text)
- `final_reels/video_segment_02.mp4` (with music + text)
- etc.

**Examples:**

```bash
# Create 5 reels (default)
./make_viral_reels.sh my_video.mp4

# Create 3 reels
./make_viral_reels.sh my_video.mp4 3

# Or use -n flag
./make_viral_reels.sh my_video.mp4 -n 3
```

---

## Using Tools Independently

You can run any tool separately:

```bash
# 1. Extract only (no music, no text)
.venv/bin/python3 extract_segments.py video.mp4 --output-dir clips/ -n 10

# 2. Add music to existing clips
.venv/bin/python3 replace_audio.py clips/*.mp4 \
    --music-dir music/viral/ --output-dir with_music/

# 3. Add text to existing videos
.venv/bin/python3 add_text_overlay.py my_video.mp4 \
    --text-file TextThoughts.txt --output-dir final/
```

---

## File Structure

```
videoed/
├── .venv/                           # Python virtual environment
├── extract_segments.py              # Tool 1
├── replace_audio.py                 # Tool 2
├── add_text_overlay.py              # Tool 3
├── make_viral_reels.sh              # Tool 4 (pipeline)
├── TextThoughts.txt                 # Text content for overlays
├── music/
│   └── viral/                       # Music files (*.mp3)
│       ├── Funky_One.mp3
│       ├── Go_Cart.mp3
│       ├── Happy_Alley.mp3
│       └── sneaky_snitch.mp3
└── final_reels/                     # Output directory
    └── (generated reels)
```

---

## Text File Format

`TextThoughts.txt` contains text segments separated by `--`:

```
First segment text.
This will be split into phrases.
Code Ninjas isnt easy.

--

Second segment text.
Another thought here.

--

Third segment text.
And so on.
```

- Tool 3 uses the **first segment only**
- Splits by periods or newlines
- Groups into 2-3 word phrases
- Times phrases evenly across video duration

---

## What About Rotation?

**Phone videos shot sideways** are usually tagged with rotation metadata. By default, these tools **preserve the rotation metadata** (don't change orientation).

If you need to rotate the video first:

```bash
# Rotate 90° clockwise (phone held right)
ffmpeg -i sideways.mp4 -vf "transpose=1" -c:a copy upright.mp4

# Rotate 90° counter-clockwise (phone held left)  
ffmpeg -i sideways.mp4 -vf "transpose=2" -c:a copy upright.mp4

# Then run pipeline on rotated video
./make_viral_reels.sh upright.mp4
```

**Transpose values:**
- `0` = 90° counter-clockwise + vertical flip
- `1` = 90° clockwise
- `2` = 90° counter-clockwise
- `3` = 90° clockwise + vertical flip

---

## Performance

**Tool 1 (Extract):** ~1x realtime for analysis (5min video = 5min processing)  
**Tool 2 (Audio):** ~instant (uses codec copy, no re-encoding)  
**Tool 3 (Text):** ~0.5-1x realtime (re-encodes video for text overlay)

**Total time for 30min video → 5 reels:** ~5-7 minutes

---

## Troubleshooting

### "No suitable segments found"

- Video is too short (need at least 10s per segment)
- Try lower `--min-duration`: `--min-duration 5`
- Try shorter `--target-duration`: `--target-duration 10`

### "ModuleNotFoundError: No module named 'av'"

- Virtual environment not set up
- Run: `python3 -m venv .venv && .venv/bin/pip install av opencv-python numpy tqdm`

### "Music directory not found"

- Check `music/viral/` exists and has `.mp3` files
- Or specify different directory: `--music-dir path/to/music/`

### "Text file not found"

- Check `TextThoughts.txt` exists in current directory
- Or specify different file: `--text-file path/to/text.txt`

---

## Next Steps

- **Add more music:** Drop `.mp3` files into `music/viral/`
- **Add more text:** Add segments to `TextThoughts.txt` (separated by `--`)
- **Tweak scoring:** Edit `extract_segments.py` weights (motion, complexity, color)
- **Different timing:** Adjust `--target-duration` for longer/shorter clips

---

## Credits

- Music generation: SciPy + NumPy (see `music_generator_example.py`)
- Music files: Incompetech (CC BY 4.0) or programmatically generated
- Text: User-provided in `TextThoughts.txt`

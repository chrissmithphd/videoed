# Current Status & Issues - 2026-06-24

## CRITICAL ISSUE: Rotation Fix Created Corrupted Video

**Problem:** `extract_reels_fixed.py` extracts rotated video but output is corrupted
- File: `reels_fixed/PXL_20260624_160111402_reel_01_score0.54.mp4` (22MB)
- Error: "moov atom not found" - file not playable
- Issue: PyAV rotation code in `_extract_segment()` method likely incomplete/incorrect

## Original Problems Identified

1. ❌ **Videos are sideways** - Phone videos (1920x1080) have 90° rotation metadata, extracted reels are landscape instead of portrait
2. ❌ **No music tested** - Music overlay researched but not working (MoviePy API issues)
3. ❌ **Two output directories** - Had reels/ and reels_test/, both removed (sideways videos)

## What Works

✅ **Basic extraction** - `extract_reels.py` works but ignores rotation
✅ **Rotation detection** - Code correctly detects 90° rotation in display matrix
✅ **Text content** - `TextThoughts.txt` has content for overlay
✅ **Text research** - Complete (see agent result in background task)

## Files

**Working:**
- `extract_reels.py` - Original extractor (no rotation handling)
- `PXL_20260624_160111402.mp4` (336MB, 140s) - Test video 1
- `PXL_20260624_160346844.mp4` (163MB, 68s) - Test video 2
- `TextThoughts.txt` - Text for overlay
- `music/calm/test_ambient.wav` - Test audio created

**Broken:**
- `extract_reels_fixed.py` - Rotation code creates corrupted output
- `reels_fixed/PXL_20260624_160111402_reel_01_score0.54.mp4` - CORRUPTED

**Documentation:**
- `RESEARCH.md` - Library research
- `MUSIC_RESEARCH.md` - Music sources
- `TEST_RESULTS.md` - Original test results (sideways videos)
- All other docs are complete

## Debug Focus

**File:** `extract_reels_fixed.py`
**Method:** `_extract_segment()` around line 300-400
**Problem area:**
```python
# Apply rotation if needed
if rotation:
    img = frame.to_ndarray(format='bgr24')
    img_rotated = rotate_frame(img, rotation)
    # Create new frame from rotated image
    new_frame = av.VideoFrame.from_ndarray(img_rotated, format='bgr24')
    new_frame.pts = frame.pts
    new_frame.time_base = frame.time_base
    frame = new_frame
```

**Issue:** Likely problems:
1. Frame PTS/time_base not set correctly
2. Encoder not flushed properly
3. Width/height swap for rotated frames
4. Rotation applied during encoding breaks encoding pipeline

## Quick Fix Options

**Option 1:** Use FFmpeg directly with transpose filter
```bash
ffmpeg -i input.mp4 -ss 115.7 -t 19.3 -vf "transpose=1" -c:v libx264 -crf 18 output.mp4
# transpose=1 = 90° clockwise
```

**Option 2:** Extract first, rotate after
1. Extract segment normally (no rotation)
2. Apply rotation in second pass with FFmpeg

**Option 3:** Fix PyAV code
- Properly handle frame timestamps during rotation
- Ensure encoder flush completes
- Test with minimal example first

## Next Session Plan

1. Try FFmpeg transpose approach (fastest)
2. If that works, update extraction script to use FFmpeg for rotation
3. Test music overlay (fix MoviePy API or use FFmpeg)
4. Implement text overlay

## Commands to Resume

```bash
cd /home/cbsmith/git/videoed
source venv/bin/activate

# Test FFmpeg rotation
ffmpeg -i PXL_20260624_160111402.mp4 -ss 115.7 -t 19.3 -vf "transpose=1" -c:v libx264 -crf 18 test_rotated.mp4

# If works, extract with rotation in one pass
ffmpeg -i PXL_20260624_160111402.mp4 -ss 115.7 -t 19.3 -vf "transpose=1" -c:v libx264 -crf 18 -c:a copy reels_fixed/test.mp4
```

## Dependencies Installed

```
opencv-python==4.13.0.92
av==17.1.0
numpy==2.5.0
tqdm==4.68.3
scenedetect==0.7
moviepy==2.2.1
scipy==1.18.0
pillow==11.3.0
```

## Key Video Specs

- Resolution: 1920x1080 (stored as landscape)
- Rotation: 90° clockwise (portrait phone video)
- Codec: HEVC (H.265)
- FPS: 30
- True orientation: 1080x1920 (portrait)

---

**TO DEBUG:** Why does PyAV rotation extraction create corrupted MP4?
**WORKAROUND:** Use FFmpeg transpose filter instead

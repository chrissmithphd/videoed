# Refactor Plan - Modular Video Tools

**Created:** 2026-06-25  
**Status:** Ready to implement  
**Context:** Session ran out of space, starting fresh

---

## Problem

Current code is tangled - rotation, music, and text all mixed together. Hard to debug.

---

## Solution: 4 Separate Tools

### Tool 1: `extract_segments.py`
**Purpose:** Find and extract interesting 10-30 second clips  
**Input:** One video file  
**Output:** Multiple video files (segments)  
**Does:**
- Analyzes for motion, complexity, color
- Finds top N interesting segments
- Extracts to separate files
- **PRESERVES original orientation** (no rotation changes)
- **PRESERVES original audio** (no audio changes)

**Usage:**
```bash
python3 extract_segments.py input.mp4 --output-dir segments/ -n 5
# Creates: segments/input_segment_01.mp4, segments/input_segment_02.mp4, etc.
```

**Base on:** `extract_reels.py` (already works for analysis)

---

### Tool 2: `replace_audio.py`
**Purpose:** Replace audio track with music  
**Input:** Video file(s) + music directory  
**Output:** New video files with replaced audio  
**Does:**
- Randomly picks music from directory
- Replaces audio track
- **NO video changes** (same resolution, orientation, frames)
- **NO re-encoding video** (use `-c:v copy` for speed)

**Usage:**
```bash
python3 replace_audio.py segments/*.mp4 --music-dir music/viral/ --output-dir with_music/
# Creates: with_music/input_segment_01.mp4 (new audio, same video)
```

**Implementation:** New script using FFmpeg `-c:v copy -map 0:v -map 1:a`

---

### Tool 3: `add_text_overlay.py`
**Purpose:** Add text overlay to videos  
**Input:** Video file(s) + text file  
**Output:** New video files with text burned in  
**Does:**
- Reads text from TextThoughts.txt (first segment)
- Splits into 2-3 word phrases
- Times phrases across video duration
- **NO orientation changes** (works on whatever orientation input is)
- **NO audio changes** (preserves existing audio with `-c:a copy`)

**Usage:**
```bash
python3 add_text_overlay.py with_music/*.mp4 --text-file TextThoughts.txt --output-dir final/
# Creates: final/input_segment_01.mp4 (with text overlay)
```

**Base on:** Working FFmpeg command from tests (3 phrases, 80pt font)

---

### Tool 4: `make_viral_reels.sh`
**Purpose:** Convenience script that chains all 3 tools  
**Input:** One video file  
**Output:** Final reels in `final_reels/`  
**Does:**
```bash
#!/bin/bash
# Step 1: Extract segments
python3 extract_segments.py "$1" --output-dir temp/segments/ -n 5

# Step 2: Add music
python3 replace_audio.py temp/segments/*.mp4 --music-dir music/viral/ --output-dir temp/with_music/

# Step 3: Add text
python3 add_text_overlay.py temp/with_music/*.mp4 --text-file TextThoughts.txt --output-dir final_reels/

echo "Done! Check final_reels/"
```

**Usage:**
```bash
./make_viral_reels.sh my_video.mp4
```

---

## What About Rotation?

**If phone video is sideways**, user can optionally run rotation tool BEFORE step 1:

```bash
# Optional: Rotate phone video first
ffmpeg -i sideways.mp4 -vf "transpose=1" -c:a copy upright.mp4

# Then run pipeline on upright video
./make_viral_reels.sh upright.mp4
```

**Or add `--rotate` flag to extract_segments.py if needed**

---

## Files to Create/Modify

### New Files:
1. `extract_segments.py` - Clean extraction (base on extract_reels.py)
2. `replace_audio.py` - Audio replacement only (NEW)
3. `add_text_overlay.py` - Text overlay only (rewrite from scratch)
4. `make_viral_reels.sh` - Convenience wrapper (NEW)

### Keep As-Is:
- `extract_reels_with_music.py` (old all-in-one, keep for reference)
- Music files in `music/viral/`
- `TextThoughts.txt`

### Test Files to Reference:
- `test_outputs/test_three_lines.mp4` - WORKING text overlay (3 phrases)
- Working FFmpeg command from session

---

## Implementation Order

**Session 2 (After /clear):**

1. **Create `replace_audio.py`** (simplest, ~30 lines)
   - Test: Take existing segment, replace audio
   - Verify: Same video, new audio, no rotation change

2. **Fix `add_text_overlay.py`** (rewrite from scratch)
   - Use WORKING command from test_three_lines.mp4
   - Test on video with music
   - Verify: Text shows, audio preserved, no rotation

3. **Clean up `extract_segments.py`** (mostly done)
   - Remove music/text code
   - Keep analysis and extraction only
   - Test: Extract 3 segments, verify original orientation preserved

4. **Create `make_viral_reels.sh`** (5 lines)
   - Chain all 3 tools
   - Test end-to-end

---

## Key Principles

✅ **Each tool does ONE thing**  
✅ **No tool changes what it shouldn't** (orientation, audio, video)  
✅ **Easy to test individually**  
✅ **Easy to debug when something breaks**  
✅ **User can run tools in any order they want**

---

## Testing Strategy

For each tool, test with `test_outputs/` files:

```bash
# Tool 1: Extract
python3 extract_segments.py PXL_20260624_160111402.mp4 --output-dir test_outputs/segments/ -n 1
# Check: Is orientation same as input? Is audio same as input?

# Tool 2: Replace audio
python3 replace_audio.py test_outputs/segments/*.mp4 --music-dir music/viral/ --output-dir test_outputs/with_music/
# Check: Is video identical? Is audio replaced? Is orientation unchanged?

# Tool 3: Add text
python3 add_text_overlay.py test_outputs/with_music/*.mp4 --text-file TextThoughts.txt --output-dir test_outputs/final/
# Check: Is text visible? Is audio unchanged? Is orientation unchanged?
```

---

## Known Working Commands

**Text overlay (3 phrases, 80pt, works):**
```bash
ffmpeg -y -i input.mp4 \
  -vf "drawtext=text='Most kids arent addicted to screens':fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:fontsize=80:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,6)',
       drawtext=text='Theyre addicted to easy':fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:fontsize=80:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,6,13)',
       drawtext=text='Code Ninjas isnt easy':fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:fontsize=80:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,13,20)'" \
  -c:a copy \
  output.mp4
```

**Audio replacement (fast):**
```bash
ffmpeg -y -i video.mp4 -i music.mp3 -map 0:v -map 1:a -c:v copy -c:a aac -shortest output.mp4
```

---

## Next Steps

1. Run `/clear` to reset context
2. Read this file: `REFACTOR_PLAN.md`
3. Start with Tool 2 (replace_audio.py) - simplest
4. Test each tool individually
5. Chain them together

---

**Current working test video:** `test_outputs/test_three_lines.mp4` has correct text overlay
**Original video:** `PXL_20260624_160111402.mp4`
**Music:** `music/viral/*.mp3` (4 tracks)

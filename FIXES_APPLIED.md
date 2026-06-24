# Video Extraction Fixes Applied

## Date: 2026-06-24

## Issues Fixed

### Bug #1: Incorrect Rotation Direction ✓ FIXED
**File:** `extract_reels_fixed.py` line 52-54
**Problem:** Used `ROTATE_90_CLOCKWISE` which made videos upside-down
**Fix:** Changed to `ROTATE_90_COUNTERCLOCKWISE`

```python
# Before (WRONG):
return cv2.rotate(frame_array, cv2.ROTATE_90_CLOCKWISE)

# After (CORRECT):
return cv2.rotate(frame_array, cv2.ROTATE_90_COUNTERCLOCKWISE)
```

### Bug #2: Timestamps Not Reset ✓ FIXED
**File:** `extract_reels_fixed.py` line 340-390
**Problem:** Kept original timestamps from source video, causing:
- Players show wrong duration (2:15 instead of 0:20)
- Videos skip/fast-forward to content
- Broken playback

**Fix:** Added PTS counters and reset timestamps to start from 0

```python
# Added after line 355:
output_video_pts = 0
output_audio_pts = 0

# Changed video frame encoding (line 367-372):
# Before (WRONG):
new_frame.pts = frame.pts         # Keeps original timestamp (e.g., 115s)
new_frame.time_base = frame.time_base

# After (CORRECT):
frame.pts = output_video_pts      # Reset to 0, 1, 2, ...
output_video_pts += 1

# Changed audio frame encoding (line 385):
# Before (WRONG):
# No PTS modification

# After (CORRECT):
frame.pts = output_audio_pts
output_audio_pts += frame.samples
```

## Verification

### Test Suite
Created comprehensive test suite in `test_outputs/`:
- **Test 01-A**: Baseline (reproduces bugs)
- **Test 01-B**: PTS fix attempt (partial)
- **Test 01-C**: 90° CW + PTS (wrong rotation)
- **Test 01-D**: 90° CCW + PTS ✓ **CORRECT**
- **Test 02**: Quick verification ✓ **CONFIRMS FIX**

### Test Results
```
Test 01-D: ✓ PASS
  - Timestamps: 0-5s (correct)
  - Resolution: 1080x1920 (portrait)
  - Rotation: Right-side-up
  - Duration: 5.0s

Test 02: ✓ PASS
  - Confirms both fixes work together
  - Ready for production use
```

## Changes Made

### Modified Files
1. `extract_reels_fixed.py` - Applied both fixes
   - Line 53: Rotation direction corrected
   - Lines 355-356: Added PTS counters
   - Lines 370-371: Reset video PTS
   - Lines 385-386: Reset audio PTS

### Test Files Created (in `test_outputs/`)
- `test_01_comprehensive.py` - Full test suite
- `test_02_verify_fix.py` - Quick verification
- `01-A_no_rotation_no_pts_fix.mp4` - Broken baseline
- `01-B_pts_fix_no_rotation.mp4` - Partial fix
- `01-C_rotation_90cw_with_pts_fix.mp4` - Wrong rotation
- `01-D_rotation_90ccw_with_pts_fix.mp4` - Correct (verified by user)
- `02_quick_verification.mp4` - Confirms fix works

## Next Steps

1. ✓ Fixes applied and verified
2. ⏳ Run full extraction: `./extract_reels_fixed.py PXL_20260624_160111402.mp4 -n 3`
3. ⏳ Verify outputs play correctly
4. ⏳ Proceed with music and text overlays

## Technical Details

### Why Counter-Clockwise?
Phone videos shot in portrait have 90° rotation metadata. The stored video is landscape (1920x1080), but should display as portrait (1080x1920). To correct this:
- The video is rotated 90° **counter-clockwise**
- This transforms landscape → portrait in the correct orientation

### Why Reset PTS?
PyAV preserves original frame timestamps by default. When extracting from the middle of a video (e.g., 115s-135s):
- Original PTS: 115s → 135s
- Players see: "Video is 2:15 long with content only at the end"
- Reset PTS: 0s → 20s
- Players see: "Video is 20s long, plays normally"

The fix resets both video and audio PTS to start from 0, ensuring proper playback.

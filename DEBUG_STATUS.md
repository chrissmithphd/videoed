# Debug Status - Video Extraction Issue

## Current Status

Created **Test 01** - systematic extraction tests with numbered outputs in `test_outputs/` directory.

## Test Results Summary

| Test | File | Timestamps | Rotation | Status |
|------|------|------------|----------|--------|
| 01-A | No rotation, no PTS fix | ✗ Wrong (70-75s) | ✗ Landscape | FAIL |
| 01-B | PTS fix, no rotation | ✗ Broken (0s) | ✗ Landscape | FAIL |
| 01-C | 90° CW + PTS fix | ✓ Correct (0-5s) | ✓ Portrait | PASS* |
| 01-D | 90° CCW + PTS fix | ✓ Correct (0-5s) | ✓ Portrait | PASS* |

*Both 01-C and 01-D pass automated checks but need manual verification for correct orientation.

## Files to Review

Located in `test_outputs/`:

1. **01-C_rotation_90cw_with_pts_fix.mp4** - 90° clockwise rotation
2. **01-D_rotation_90ccw_with_pts_fix.mp4** - 90° counter-clockwise rotation

**Action needed:** Play both files and report which one is right-side-up.

## Bugs Confirmed

### Bug #1: Timestamp Reset Missing
**Location:** `extract_reels_fixed.py` line 368-369
```python
# Current (BROKEN):
new_frame.pts = frame.pts  # Keeps original timestamps from source video
```

**Effect:** 
- Videos show wrong duration in players (2:15 instead of 0:19)
- Players may skip/fast-forward to find content

### Bug #2: Rotation Direction Unknown
Need manual verification to confirm if 90° clockwise or counter-clockwise is correct for portrait phone videos.

## Test Script

All tests run from: `test_outputs/test_01_comprehensive.py`

Each test extracts 5 seconds with different configurations to isolate the bugs.

## Next Steps

1. **You:** Play 01-C and 01-D, report which is correctly oriented
2. **Me:** Apply the working fix to `extract_reels_fixed.py`
3. **Test:** Re-run full extraction on original video
4. **Verify:** Confirm output plays correctly with proper duration

## Notes

- All test outputs isolated in `test_outputs/` directory
- Numbered tests (01, 02, etc.) for easy tracking
- Original source videos remain in root directory
- Test scripts included for reproducibility

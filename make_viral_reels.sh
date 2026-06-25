#!/bin/bash
# Tool 4: Convenience script that chains all 3 tools
#
# Usage:
#   ./make_viral_reels.sh my_video.mp4
#   ./make_viral_reels.sh my_video.mp4 -n 3   # Extract 3 segments
#
# Output: final_reels/

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$SCRIPT_DIR/.venv/bin/python3"

# Check if venv exists
if [ ! -f "$PYTHON" ]; then
    echo "ERROR: Virtual environment not found at .venv/"
    echo "Run: python3 -m venv .venv && .venv/bin/pip install av opencv-python numpy tqdm"
    exit 1
fi

# Parse arguments
INPUT_VIDEO="$1"
NUM_SEGMENTS="${2:-5}"  # Default to 5 segments

if [ -z "$INPUT_VIDEO" ]; then
    echo "Usage: $0 <video_file> [num_segments]"
    echo ""
    echo "Example:"
    echo "  $0 my_video.mp4       # Extract 5 segments (default)"
    echo "  $0 my_video.mp4 3     # Extract 3 segments"
    exit 1
fi

if [ ! -f "$INPUT_VIDEO" ]; then
    echo "ERROR: Video file not found: $INPUT_VIDEO"
    exit 1
fi

# Parse -n flag if present
if [ "$2" = "-n" ]; then
    NUM_SEGMENTS="$3"
elif [ "$2" != "" ] && [ "$2" != "-n" ]; then
    NUM_SEGMENTS="$2"
fi

echo "=================================================="
echo "VideoReel Generator Pipeline"
echo "=================================================="
echo "Input: $INPUT_VIDEO"
echo "Output: final_reels/"
echo "Segments: $NUM_SEGMENTS"
echo ""

# Step 1: Extract segments
echo "STEP 1/3: Extracting interesting segments..."
$PYTHON "$SCRIPT_DIR/extract_segments.py" "$INPUT_VIDEO" \
    --output-dir temp/segments/ -n "$NUM_SEGMENTS"

# Check if extraction succeeded
if [ ! -d "temp/segments/" ] || [ -z "$(ls -A temp/segments/)" ]; then
    echo "ERROR: No segments extracted. Check if video is long enough (>10s per segment)."
    exit 1
fi

echo ""
echo "STEP 2/3: Replacing audio with viral music..."
$PYTHON "$SCRIPT_DIR/replace_audio.py" temp/segments/*.mp4 \
    --music-dir music/viral/ --output-dir temp/with_music/

echo ""
echo "STEP 3/3: Adding text overlay..."
$PYTHON "$SCRIPT_DIR/add_text_overlay.py" temp/with_music/*.mp4 \
    --text-file TextThoughts.txt --output-dir final_reels/

echo ""
echo "=================================================="
echo "✓ DONE!"
echo "=================================================="
echo ""
echo "Output files:"
ls -lh final_reels/

echo ""
echo "Cleaning up temporary files..."
rm -rf temp/

echo ""
echo "Final reels ready in: final_reels/"

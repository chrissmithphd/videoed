#!/bin/bash
# Quick test of tools 2 & 3 (skip slow extraction)
# Uses existing short test video

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$SCRIPT_DIR/.venv/bin/python3"

echo "=========================================="
echo "Quick Pipeline Test (Tools 2 & 3)"
echo "=========================================="
echo ""

# Use existing short test video
TEST_VIDEO="test_outputs/11_final_working.mp4"

if [ ! -f "$TEST_VIDEO" ]; then
    echo "ERROR: Test video not found: $TEST_VIDEO"
    exit 1
fi

# Clean previous test
rm -rf test_pipeline_output/
mkdir -p test_pipeline_output/step1/

# Copy test video to simulate extraction output
cp "$TEST_VIDEO" test_pipeline_output/step1/test_segment_01.mp4

echo "Step 1/2: Replace audio with music..."
$PYTHON replace_audio.py test_pipeline_output/step1/*.mp4 \
    --music-dir music/viral/ \
    --output-dir test_pipeline_output/step2/

echo ""
echo "Step 2/2: Add text overlay..."
$PYTHON add_text_overlay.py test_pipeline_output/step2/*.mp4 \
    --text-file TextThoughts.txt \
    --output-dir test_pipeline_output/final/

echo ""
echo "=========================================="
echo "✓ DONE!"
echo "=========================================="
echo ""
echo "Output:"
ls -lh test_pipeline_output/final/

echo ""
echo "Check the video:"
echo "  ffplay test_pipeline_output/final/test_segment_01.mp4"

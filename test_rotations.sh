#!/bin/bash
# Test all 4 rotation options quickly
ffmpeg -y -ss 115 -t 5 -i PXL_20260624_160111402.mp4 -vf "transpose=0" -an test_outputs/rot_0.mp4 2>/dev/null
ffmpeg -y -ss 115 -t 5 -i PXL_20260624_160111402.mp4 -vf "transpose=1" -an test_outputs/rot_1.mp4 2>/dev/null
ffmpeg -y -ss 115 -t 5 -i PXL_20260624_160111402.mp4 -vf "transpose=2" -an test_outputs/rot_2.mp4 2>/dev/null
ffmpeg -y -ss 115 -t 5 -i PXL_20260624_160111402.mp4 -vf "transpose=3" -an test_outputs/rot_3.mp4 2>/dev/null
echo "Created 4 test files (5s each):"
echo "rot_0.mp4 = transpose=0 (90° clockwise)"
echo "rot_1.mp4 = transpose=1 (90° counter-clockwise)" 
echo "rot_2.mp4 = transpose=2 (90° counter-clockwise + flip)"
echo "rot_3.mp4 = transpose=3 (90° clockwise + flip)"

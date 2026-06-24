#!/usr/bin/env python3
"""Simple text overlay - takes first segment from TextThoughts.txt"""
import sys
import subprocess
from pathlib import Path

def read_first_segment(text_file):
    """Read first text segment from file (split by --)"""
    with open(text_file) as f:
        content = f.read()
    segments = [s.strip() for s in content.split('--') if s.strip()]
    if not segments:
        raise ValueError("No segments found")
    
    # Get first segment, split into lines, remove apostrophes
    lines = [line.strip().replace("'", "").replace("'", "") 
             for line in segments[0].split('\n') if line.strip()]
    return lines[:3]  # First 3 lines

def create_overlay(input_video, output_video, text_lines):
    """Create video with text overlay"""
    duration = 20  # Assume 20s video
    time_per_line = duration / len(text_lines)
    
    filters = []
    for i, text in enumerate(text_lines):
        start = i * time_per_line
        end = (i + 1) * time_per_line
        
        filter_text = f"drawtext=text='{text}':fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:fontsize=80:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{start:.1f},{end:.1f})'"
        filters.append(filter_text)
    
    vf = ','.join(filters)
    
    cmd = [
        'ffmpeg', '-y',
        '-i', input_video,
        '-vf', vf,
        '-c:a', 'copy',
        output_video
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Created: {output_video}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python add_text_simple.py input.mp4 output.mp4")
        sys.exit(1)
    
    lines = read_first_segment('TextThoughts.txt')
    print(f"Using text lines: {lines}")
    create_overlay(sys.argv[1], sys.argv[2], lines)

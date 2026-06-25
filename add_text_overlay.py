#!/usr/bin/env python3
"""
Add text overlay to videos using first text segment from TextThoughts.txt.

Usage:
    python3 add_text_overlay.py video1.mp4 --text-file TextThoughts.txt --output-dir final/
    python3 add_text_overlay.py with_music/*.mp4 --text-file TextThoughts.txt --output-dir final/

Features:
    - Splits first text segment into 2-3 word phrases
    - Times phrases evenly across video duration
    - 80pt white text with black border, centered
    - Preserves audio (no audio changes)
    - Works on any video orientation
"""

import argparse
import subprocess
import re
from pathlib import Path


def load_all_segments(text_file):
    """Load all text segments from file."""
    text_path = Path(text_file)
    if not text_path.exists():
        raise FileNotFoundError(f"Text file not found: {text_file}")

    with open(text_path, "r") as f:
        content = f.read()

    # Split by --
    segments = content.split("--")
    if not segments:
        raise ValueError("No text segments found")

    # Clean up segments and filter empty ones
    cleaned_segments = []
    for seg in segments:
        cleaned = seg.strip()
        if cleaned:
            cleaned_segments.append(cleaned)

    if not cleaned_segments:
        raise ValueError("No valid text segments found")

    return cleaned_segments


def split_into_phrases(text, max_words_per_phrase=3):
    """Split text into short phrases (2-3 words each)."""
    # Split by lines or periods
    lines = text.replace(".", "\n").split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    # Split each line into phrases
    phrases = []
    for line in lines:
        words = line.split()
        for i in range(0, len(words), max_words_per_phrase):
            phrase = " ".join(words[i:i+max_words_per_phrase])
            phrases.append(phrase)

    return phrases


def get_video_duration(video_path):
    """Get video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Could not get duration for {video_path}")

    return float(result.stdout.strip())


def create_drawtext_filter(phrases, video_duration):
    """Create FFmpeg drawtext filter for timed phrases."""
    if not phrases:
        raise ValueError("No phrases to display")

    # Calculate timing for each phrase
    time_per_phrase = video_duration / len(phrases)

    # Font settings
    font_file = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    font_size = 80
    font_color = "white"
    border_width = 5
    border_color = "black"

    # Build drawtext filter for each phrase
    filters = []
    for i, phrase in enumerate(phrases):
        # Escape special characters for FFmpeg
        escaped_phrase = phrase.replace("'", "'\\\\\\''")

        start_time = i * time_per_phrase
        end_time = (i + 1) * time_per_phrase

        drawtext = (
            f"drawtext=text='{escaped_phrase}':"
            f"fontfile={font_file}:"
            f"fontsize={font_size}:"
            f"fontcolor={font_color}:"
            f"borderw={border_width}:"
            f"bordercolor={border_color}:"
            f"x=(w-text_w)/2:"  # Center horizontally
            f"y=(h-text_h)/2:"  # Center vertically
            f"enable='between(t,{start_time:.2f},{end_time:.2f})'"
        )
        filters.append(drawtext)

    # Join all filters with comma
    return ",".join(filters)


def add_text_overlay(video_path, text_filter, output_path):
    """Add text overlay to video using FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", text_filter,
        "-c:a", "copy",  # Preserve audio
        str(output_path)
    ]

    print(f"Processing: {video_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        raise RuntimeError(f"FFmpeg failed for {video_path}")

    print(f"  ✓ Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Add text overlay to videos")
    parser.add_argument("videos", nargs="+", help="Input video files")
    parser.add_argument("--text-file", required=True, help="Text file (cycles through all segments)")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--max-words", type=int, default=3, help="Max words per phrase (default: 3)")

    args = parser.parse_args()

    # Setup
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all text segments
    all_segments = load_all_segments(args.text_file)

    print(f"Loaded {len(all_segments)} text segments from {args.text_file}")
    print(f"Processing {len(args.videos)} videos...")
    print()

    # Process each video with cycling through segments
    for video_idx, video_str in enumerate(args.videos):
        video_path = Path(video_str)
        if not video_path.exists():
            print(f"WARNING: Skipping {video_str} (not found)")
            continue

        # Cycle through segments (wrap around if more videos than segments)
        segment_idx = video_idx % len(all_segments)
        segment_text = all_segments[segment_idx]
        phrases = split_into_phrases(segment_text, args.max_words)

        print(f"Video {video_idx + 1}/{len(args.videos)}: {video_path.name}")
        print(f"  Using text segment {segment_idx + 1}/{len(all_segments)} ({len(phrases)} phrases)")

        try:
            # Get video duration
            duration = get_video_duration(video_path)

            # Create text filter
            text_filter = create_drawtext_filter(phrases, duration)

            # Create output path
            output_path = output_dir / video_path.name

            # Add text overlay
            add_text_overlay(video_path, text_filter, output_path)

        except Exception as e:
            print(f"ERROR processing {video_path.name}: {e}")
            continue

        print()

    print(f"Done! Check {args.output_dir}/")


if __name__ == "__main__":
    main()

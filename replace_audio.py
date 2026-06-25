#!/usr/bin/env python3
"""
Replace audio in video files with random music from a directory.

Usage:
    python3 replace_audio.py video1.mp4 video2.mp4 --music-dir music/viral/ --output-dir with_music/
    python3 replace_audio.py segments/*.mp4 --music-dir music/viral/ --output-dir with_music/

Features:
    - Replaces audio track only (video untouched, no re-encoding)
    - Random music selection from directory
    - Preserves video orientation and quality
    - Fast: uses -c:v copy (no video re-encode)
"""

import argparse
import random
import subprocess
from pathlib import Path


def get_music_files(music_dir):
    """Find all music files in directory."""
    music_path = Path(music_dir)
    if not music_path.exists():
        raise FileNotFoundError(f"Music directory not found: {music_dir}")

    music_files = list(music_path.glob("*.mp3")) + list(music_path.glob("*.wav"))
    if not music_files:
        raise FileNotFoundError(f"No music files found in {music_dir}")

    return music_files


def replace_audio(video_path, music_path, output_path):
    """Replace video audio with music using FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),  # Input video
        "-i", str(music_path),  # Input audio
        "-map", "0:v",          # Take video from first input
        "-map", "1:a",          # Take audio from second input
        "-c:v", "copy",         # Copy video stream (no re-encode)
        "-c:a", "aac",          # Re-encode audio to AAC
        "-shortest",            # Match shortest stream (audio or video)
        str(output_path)
    ]

    print(f"Processing: {video_path.name} + {music_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        raise RuntimeError(f"FFmpeg failed for {video_path}")

    print(f"  ✓ Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Replace video audio with music")
    parser.add_argument("videos", nargs="+", help="Input video files")
    parser.add_argument("--music-dir", required=True, help="Directory with music files")
    parser.add_argument("--output-dir", required=True, help="Output directory")

    args = parser.parse_args()

    # Setup
    music_files = get_music_files(args.music_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(music_files)} music files in {args.music_dir}")
    print(f"Processing {len(args.videos)} videos...")
    print()

    # Process each video
    for video_str in args.videos:
        video_path = Path(video_str)
        if not video_path.exists():
            print(f"WARNING: Skipping {video_str} (not found)")
            continue

        # Pick random music
        music_path = random.choice(music_files)

        # Create output path (same name as input)
        output_path = output_dir / video_path.name

        try:
            replace_audio(video_path, music_path, output_path)
        except Exception as e:
            print(f"ERROR processing {video_path.name}: {e}")
            continue

    print()
    print(f"Done! Check {args.output_dir}/")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Add music to extracted video segments using FFmpeg.
Separate from rotation/analysis logic.
"""

import subprocess
import json
from pathlib import Path
import random
import argparse


def get_music_files(music_dir: Path) -> list:
    """Get list of available music files"""
    if not music_dir.exists():
        return []
    
    music_files = []
    for ext in ['*.mp3', '*.wav', '*.ogg', '*.m4a']:
        music_files.extend(music_dir.glob(ext))
    
    return sorted(music_files)


def add_music_with_ffmpeg(
    input_video: Path,
    output_video: Path,
    music_file: Path,
    music_volume: float = 0.3,
    music_start_offset: float = 0.0
):
    """
    Add music to video using FFmpeg (no rotation - that's done separately).
    
    Args:
        input_video: Input video file (already rotation-corrected)
        output_video: Output video file
        music_file: Music file to overlay
        music_volume: Volume level (0.0-1.0)
        music_start_offset: Skip N seconds of music intro
    """
    
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite
        '-i', str(input_video),  # Video input
    ]
    
    # Music input with optional offset
    if music_start_offset > 0:
        cmd.extend(['-ss', str(music_start_offset)])
    
    cmd.extend([
        '-stream_loop', '-1',  # Loop music
        '-i', str(music_file),  # Music input
        '-shortest',  # Stop when video ends
        '-map', '0:v:0',  # Video from input 0
        '-map', '1:a:0',  # Audio from input 1 (music)
        '-c:v', 'copy',  # Copy video (no re-encode)
        '-c:a', 'aac',
        '-b:a', '192k',
        '-filter:a', f'volume={music_volume}',
        str(output_video)
    ])
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr}")


def main():
    parser = argparse.ArgumentParser(
        description='Add music to extracted video segments'
    )
    parser.add_argument('segments', help='segments_analysis.json from extract_reels.py')
    parser.add_argument('--music-dir', type=Path, default=Path('music/viral'),
                       help='Directory with music files (default: music/viral/)')
    parser.add_argument('--music-volume', type=float, default=0.3,
                       help='Music volume (0.0-1.0, default: 0.3)')
    parser.add_argument('--music-offset', type=float, default=0.0,
                       help='Skip N seconds of music intro (default: 0)')
    parser.add_argument('-o', '--output-dir', type=Path, default=Path('reels'),
                       help='Output directory (default: reels/)')
    
    args = parser.parse_args()
    
    # Load analysis
    with open(args.segments) as f:
        analysis = json.load(f)
    
    # Get music files
    music_files = get_music_files(args.music_dir)
    if not music_files:
        print(f"Error: No music files found in {args.music_dir}")
        return
    
    print(f"Found {len(music_files)} music track(s)")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nAdding music to segments...")
    print("=" * 70)
    
    for video_path, data in analysis.items():
        video_name = Path(video_path).stem
        segments = data['segments']
        
        print(f"\nProcessing: {video_name} ({len(segments)} segments)")
        
        for idx, segment in enumerate(segments):
            # Pick random music
            music_file = random.choice(music_files)
            
            # TODO: Extract segment from original video first
            # For now, assume segments are already extracted
            input_segment = args.output_dir / f"{video_name}_segment_{idx+1:02d}.mp4"
            output_path = args.output_dir / f"{video_name}_reel_{idx+1:02d}_score{segment['score']:.2f}.mp4"
            
            if not input_segment.exists():
                print(f"  ⚠ Skipping: {input_segment.name} (not found)")
                print(f"     Run extract with FFmpeg first to create base segments")
                continue
            
            try:
                add_music_with_ffmpeg(
                    input_segment,
                    output_path,
                    music_file,
                    args.music_volume,
                    args.music_offset
                )
                
                print(f"  ✓ {output_path.name} (music: {music_file.stem})")
            
            except Exception as e:
                print(f"  ✗ Failed: {e}")
    
    print("\n" + "=" * 70)
    print(f"✓ Complete! Reels saved to: {args.output_dir}/")


if __name__ == '__main__':
    main()

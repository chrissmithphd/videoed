#!/usr/bin/env python3
"""
Test 10 - Simplest Audio Approach
Just use ffmpeg subprocess - PyAV audio encoding is too complex
"""

import subprocess
import av
from pathlib import Path


def extract_with_ffmpeg_audio(video_input: str, audio_input: str, start_time: float, duration: float, output_path: str):
    """
    Use ffmpeg to:
    1. Extract video segment with rotation
    2. Extract audio segment and loop it
    3. Combine them

    This is WAY simpler than PyAV audio encoding
    """
    print(f"\nExtracting {duration}s segment with ffmpeg...")
    print(f"  Video: {video_input} @ {start_time:.1f}s")
    print(f"  Audio: {audio_input}")

    # Step 1: Extract rotated video (no audio)
    temp_video = output_path.replace('.mp4', '_video_only.mp4')

    cmd_video = [
        'ffmpeg', '-y',
        '-ss', str(start_time),
        '-i', video_input,
        '-t', str(duration),
        '-vf', 'transpose=2',  # transpose=2 is 90° CCW
        '-c:v', 'libx264',
        '-crf', '18',
        '-an',  # No audio
        temp_video
    ]

    print("Step 1: Extracting rotated video...")
    try:
        subprocess.run(cmd_video, check=True, capture_output=True)
        print(f"  ✓ Created temp video: {temp_video}")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ FFmpeg error: {e.stderr.decode()}")
        return False

    # Step 2: Combine video with audio (ffmpeg will loop audio automatically if too short)
    cmd_combine = [
        'ffmpeg', '-y',
        '-i', temp_video,
        '-stream_loop', '-1',  # Loop audio indefinitely
        '-i', audio_input,
        '-t', str(duration),  # Limit to video duration
        '-c:v', 'copy',  # Copy video (already encoded)
        '-c:a', 'aac',  # Encode audio to AAC
        '-b:a', '192k',  # Audio bitrate
        '-shortest',  # Stop at shortest stream
        output_path
    ]

    print("Step 2: Adding audio...")
    try:
        subprocess.run(cmd_combine, check=True, capture_output=True)
        print(f"  ✓ Created final video: {output_path}")

        # Clean up temp file
        Path(temp_video).unlink()
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ FFmpeg error: {e.stderr.decode()}")
        return False


def verify_complete(path: str):
    """Quick verification"""
    print(f"\nVerifying: {path}")

    c = av.open(path)
    v = c.streams.video[0]
    a = c.streams.audio[0] if c.streams.audio else None

    # Count frames
    video_frames = list(c.decode(video=0))

    c.close()

    print(f"  Resolution: {v.width}x{v.height}")
    print(f"  Video frames: {len(video_frames)}")
    print(f"  Video duration: {video_frames[-1].time - video_frames[0].time:.2f}s")

    if a:
        print(f"  Audio: {a.rate}Hz, {a.channels} channels, {a.codec_context.name}")
        print(f"  ✓ Has audio!")
        return True
    else:
        print(f"  ✗ No audio!")
        return False


def main():
    project_root = Path(__file__).parent.parent
    input_video = project_root / "PXL_20260624_160111402.mp4"
    audio_file = project_root / "music/lofi/floating_cities.mp3"
    output_path = project_root / "test_outputs/10_ffmpeg_audio.mp4"

    if not input_video.exists():
        print(f"Error: {input_video} not found")
        return

    if not audio_file.exists():
        print(f"Error: {audio_file} not found")
        return

    # Get video info
    container = av.open(str(input_video))
    duration_total = float(container.streams.video[0].duration * container.streams.video[0].time_base)
    container.close()

    start_time = duration_total / 2.0
    duration = 5.0

    print(f"{'='*60}")
    print(f"Test 10: Simple FFmpeg Audio Approach")
    print(f"{'='*60}")

    success = extract_with_ffmpeg_audio(
        str(input_video),
        str(audio_file),
        start_time,
        duration,
        str(output_path)
    )

    if success and output_path.exists():
        if verify_complete(str(output_path)):
            print(f"\n✓✓ SUCCESS!")
            print(f"\nPlay {output_path.name} - you should hear music!")
        else:
            print(f"\n✗ Verification failed")
    else:
        print(f"\n✗ Extraction failed")


if __name__ == '__main__':
    main()

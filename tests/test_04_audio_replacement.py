#!/usr/bin/env python3
"""
Test 04 - Audio Replacement
Replace original video audio with background music
"""

import av
from pathlib import Path
import subprocess


def replace_audio_pyav(video_path: str, audio_path: str, output_path: str):
    """Replace video audio using PyAV (frame-by-frame)"""
    print(f"Replacing audio with PyAV...")
    print(f"  Video: {video_path}")
    print(f"  Audio: {audio_path}")

    video_container = av.open(video_path)
    audio_container = av.open(audio_path)
    output_container = av.open(output_path, 'w')

    try:
        # Copy video stream settings
        input_video = video_container.streams.video[0]
        output_video = output_container.add_stream('libx264', rate=input_video.average_rate)
        output_video.width = input_video.width
        output_video.height = input_video.height
        output_video.pix_fmt = 'yuv420p'
        output_video.options = {'crf': '18', 'preset': 'medium'}

        # Copy NEW audio stream settings
        input_audio = audio_container.streams.audio[0]
        # Use same codec as input audio
        output_audio = output_container.add_stream(
            input_audio.codec_context.name,
            rate=input_audio.rate
        )

        # Get video duration
        video_duration = float(input_video.duration * input_video.time_base)
        print(f"  Video duration: {video_duration:.2f}s")

        # Reset PTS counters
        output_video_pts = 0
        output_audio_pts = 0

        # Demux and mux video
        print("  Processing video...")
        for packet in video_container.demux(video=0):
            for frame in packet.decode():
                frame.pts = output_video_pts
                output_video_pts += 1

                for new_packet in output_video.encode(frame):
                    output_container.mux(new_packet)

        # Demux and mux audio (loop if needed)
        print("  Processing audio...")
        audio_duration = 0
        while audio_duration < video_duration:
            audio_container.seek(0)  # Restart audio if needed

            for packet in audio_container.demux(audio=0):
                for frame in packet.decode():
                    if audio_duration >= video_duration:
                        break

                    frame.pts = output_audio_pts
                    output_audio_pts += frame.samples
                    audio_duration = output_audio_pts / input_audio.rate

                    for new_packet in output_audio.encode(frame):
                        output_container.mux(new_packet)

                if audio_duration >= video_duration:
                    break

        # Flush
        for packet in output_video.encode(None):
            output_container.mux(packet)
        for packet in output_audio.encode(None):
            output_container.mux(packet)

        print(f"✓ Created: {output_path}")

    finally:
        video_container.close()
        audio_container.close()
        output_container.close()


def replace_audio_ffmpeg(video_path: str, audio_path: str, output_path: str):
    """Replace video audio using FFmpeg (much faster and simpler)"""
    print(f"Replacing audio with FFmpeg...")
    print(f"  Video: {video_path}")
    print(f"  Audio: {audio_path}")

    # FFmpeg command to replace audio
    # -i video.mp4  = input video
    # -i audio.wav  = input audio
    # -c:v copy     = copy video codec (no re-encode)
    # -map 0:v      = use video from first input
    # -map 1:a      = use audio from second input
    # -shortest     = stop when shortest stream ends
    cmd = [
        'ffmpeg', '-y',  # overwrite output
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',  # Copy video - NO re-encoding!
        '-map', '0:v',   # Video from input 0
        '-map', '1:a',   # Audio from input 1
        '-shortest',     # Stop at shortest stream
        output_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ Created: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ FFmpeg error: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"✗ FFmpeg not found - install with: sudo apt install ffmpeg")
        return False


def verify_audio_replacement(video_path: str):
    """Verify the audio was replaced correctly"""
    print(f"\nVerifying: {video_path}")

    try:
        container = av.open(video_path)
        video_stream = container.streams.video[0]
        audio_stream = container.streams.audio[0] if container.streams.audio else None

        print(f"  Video: {video_stream.width}x{video_stream.height}, {video_stream.duration * video_stream.time_base:.2f}s")

        if audio_stream:
            print(f"  Audio: {audio_stream.rate}Hz, {audio_stream.channels} channels")
            print(f"  Audio codec: {audio_stream.codec_context.name}")
            print(f"  ✓ Has audio stream")
        else:
            print(f"  ✗ No audio stream found!")
            return False

        container.close()
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    # Use one of the correctly extracted test videos
    test_video = "01-D_rotation_90ccw_with_pts_fix.mp4"
    if not Path(test_video).exists():
        print(f"Error: Test video {test_video} not found")
        print("Run test_01_comprehensive.py first")
        return

    # Test all three music styles
    music_files = [
        ("../music/calm/bgm_melody.wav", "melody"),
        ("../music/calm/bgm_pad.wav", "pad"),
        ("../music/calm/bgm_arpeggio.wav", "arpeggio"),
    ]

    print("=" * 60)
    print("Test 04: Audio Replacement")
    print("=" * 60)

    results = []

    for audio_path, style in music_files:
        if not Path(audio_path).exists():
            print(f"\n✗ Audio file not found: {audio_path}")
            print("Run test_03_create_better_music.py first")
            continue

        output_path = f"04_{style}_audio_replaced.mp4"

        print(f"\n{'='*60}")
        print(f"Testing with {style} music")
        print(f"{'='*60}")

        # Try PyAV (ffmpeg not installed)
        try:
            replace_audio_pyav(test_video, audio_path, output_path)
            success = True
        except Exception as e:
            print(f"✗ PyAV failed: {e}")
            success = False

        if success and Path(output_path).exists():
            verify_success = verify_audio_replacement(output_path)
            results.append((style, output_path, verify_success))
        else:
            results.append((style, output_path, False))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for style, path, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {path} ({style})")

    if any(success for _, _, success in results):
        print(f"\n✓ Audio replacement working!")
        print(f"\nPlay the files to choose which music style you prefer:")
        for style, path, success in results:
            if success:
                print(f"  - {path} ({style})")
    else:
        print(f"\n✗ All tests failed")


if __name__ == '__main__':
    main()

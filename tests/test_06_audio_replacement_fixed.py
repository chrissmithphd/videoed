#!/usr/bin/env python3
"""
Test 06 - Audio Replacement with Proper PTS
Replace audio AND fix the PTS properly so duration is correct
"""

import av
import cv2
import numpy as np
from pathlib import Path


def extract_and_replace_audio(video_input: str, audio_input: str, start_time: float, output_path: str):
    """
    Extract video segment with rotation, proper PTS reset, AND replace audio
    This combines all fixes: rotation, PTS, and audio replacement
    """
    print(f"\nExtracting 5s segment with audio replacement...")
    print(f"  Video: {video_input} @ {start_time:.1f}s")
    print(f"  Audio: {audio_input}")

    video_container = av.open(video_input)
    audio_container = av.open(audio_input)
    output_container = av.open(output_path, 'w')

    try:
        input_video = video_container.streams.video[0]

        # Swap dimensions for 90° rotation
        output_width = input_video.height
        output_height = input_video.width

        output_video = output_container.add_stream('libx264', rate=input_video.average_rate)
        output_video.width = output_width
        output_video.height = output_height
        output_video.pix_fmt = 'yuv420p'
        output_video.options = {'crf': '18', 'preset': 'medium'}

        # Use NEW audio from audio file - encode to AAC for MP4 compatibility
        input_audio = audio_container.streams.audio[0]
        output_audio = output_container.add_stream('aac', rate=44100)

        end_time = start_time + 5.0
        seek_point = int(start_time * av.time_base)
        video_container.seek(seek_point)

        # Track first PTS for proper reset
        first_video_pts = None
        first_audio_pts = None

        video_frame_count = 0

        # Process video with rotation and proper PTS
        print("  Processing video...")
        for packet in video_container.demux(video=0):
            for frame in packet.decode():
                if frame.time < start_time:
                    continue
                if frame.time > end_time:
                    break

                # Store original PTS
                original_pts = frame.pts
                original_time_base = frame.time_base

                # Apply rotation
                img = frame.to_ndarray(format='bgr24')
                img_rotated = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                new_frame = av.VideoFrame.from_ndarray(img_rotated, format='bgr24')

                # Proper PTS reset
                if first_video_pts is None:
                    first_video_pts = original_pts

                new_frame.pts = original_pts - first_video_pts
                new_frame.time_base = original_time_base

                video_frame_count += 1

                for encoded_packet in output_video.encode(new_frame):
                    output_container.mux(encoded_packet)

                if frame.time >= end_time:
                    break

        print(f"  Encoded {video_frame_count} video frames")

        # Process NEW audio (loop if needed to match video duration)
        print("  Processing audio...")
        video_duration = 5.0
        audio_duration = 0.0
        audio_frame_count = 0

        while audio_duration < video_duration:
            audio_container.seek(0)  # Restart audio if needed

            for packet in audio_container.demux(audio=0):
                for frame in packet.decode():
                    if audio_duration >= video_duration:
                        break

                    # Proper PTS reset for audio
                    if first_audio_pts is None:
                        first_audio_pts = frame.pts

                    # Calculate offset PTS
                    current_offset = frame.pts - first_audio_pts
                    frame.pts = current_offset

                    audio_duration = frame.pts / input_audio.rate
                    audio_frame_count += 1

                    for encoded_packet in output_audio.encode(frame):
                        output_container.mux(encoded_packet)

                if audio_duration >= video_duration:
                    break

        print(f"  Encoded {audio_frame_count} audio frames")

        # Flush encoders
        for packet in output_video.encode(None):
            output_container.mux(packet)
        for packet in output_audio.encode(None):
            output_container.mux(packet)

        print(f"✓ Created: {output_path}")

    finally:
        video_container.close()
        audio_container.close()
        output_container.close()


def verify_complete(path: str):
    """Verify video has correct duration, rotation, and audio"""
    print(f"\nVerifying: {path}")

    try:
        c = av.open(path)
        v = c.streams.video[0]
        a = c.streams.audio[0] if c.streams.audio else None

        # Decode all frames
        video_frames = []
        for frame in c.decode(video=0):
            video_frames.append(frame.time)

        c.close()

        if not video_frames:
            print(f"  ✗ No video frames!")
            return False

        duration = video_frames[-1] - video_frames[0]

        print(f"  Resolution: {v.width}x{v.height}")
        print(f"  Video frames: {len(video_frames)}")
        print(f"  Duration: {duration:.3f}s")
        print(f"  First timestamp: {video_frames[0]:.3f}s")
        print(f"  Last timestamp: {video_frames[-1]:.3f}s")

        if a:
            print(f"  Audio: {a.rate}Hz, {a.channels} channels")
            print(f"  Audio codec: {a.codec_context.name}")

        # Check all criteria
        issues = []

        if v.width != 1080 or v.height != 1920:
            issues.append(f"Wrong resolution (should be 1080x1920)")

        if len(video_frames) < 135:  # ~150 frames expected at 30fps
            issues.append(f"Too few frames ({len(video_frames)}, expected ~150)")

        if video_frames[0] > 0.1:
            issues.append(f"Start time too high ({video_frames[0]:.3f}s)")

        if duration < 4.5 or duration > 5.5:
            issues.append(f"Duration wrong ({duration:.3f}s, should be ~5s)")

        if not a:
            issues.append("No audio stream")

        if issues:
            print(f"\n  ✗ ISSUES:")
            for issue in issues:
                print(f"    - {issue}")
            return False
        else:
            print(f"\n  ✓ ALL CHECKS PASS")
            return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    input_video = "../PXL_20260624_160111402.mp4"

    # Test all 3 music styles
    music_files = [
        ("../music/calm/bgm_melody.wav", "melody", "Pleasant melody"),
        ("../music/calm/bgm_pad.wav", "pad", "Soft ambient pad"),
        ("../music/calm/bgm_arpeggio.wav", "arpeggio", "Gentle arpeggio"),
    ]

    if not Path(input_video).exists():
        print(f"Error: {input_video} not found")
        return

    # Get video duration
    container = av.open(input_video)
    duration = float(container.streams.video[0].duration * container.streams.video[0].time_base)
    container.close()

    print(f"Input video: {duration:.1f}s")
    start_time = duration / 2.0

    print(f"\n{'='*60}")
    print(f"Test 06: Complete Pipeline - Rotation + PTS + Audio")
    print(f"{'='*60}")

    results = []

    for audio_path, style, description in music_files:
        if not Path(audio_path).exists():
            print(f"\n✗ Audio not found: {audio_path}")
            print("Run test_03_create_better_music.py first")
            continue

        output_path = f"06_{style}_complete.mp4"

        print(f"\n{'='*60}")
        print(f"Testing {style}: {description}")
        print(f"{'='*60}")

        try:
            extract_and_replace_audio(input_video, audio_path, start_time, output_path)

            if Path(output_path).exists():
                success = verify_complete(output_path)
                results.append((style, output_path, success))
            else:
                results.append((style, output_path, False))
        except Exception as e:
            print(f"✗ Failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((style, output_path, False))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for style, path, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {path}")

    if any(success for _, _, success in results):
        print(f"\n✓✓ Complete pipeline working!")
        print(f"\nPlay these files - they should have:")
        print(f"  - Correct portrait rotation")
        print(f"  - 5 second duration")
        print(f"  - Replaced background music")
        print(f"\nFiles:")
        for style, path, success in results:
            if success:
                print(f"  - {path}")
    else:
        print(f"\n✗✗ All tests failed - iterating...")


if __name__ == '__main__':
    main()

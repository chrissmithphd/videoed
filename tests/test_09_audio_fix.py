#!/usr/bin/env python3
"""
Test 09 - Fix Audio Duration Calculation
The audio was only encoding 2 frames because duration calculation was wrong
"""

import av
import cv2
import numpy as np
from pathlib import Path


def extract_with_working_audio(video_input: str, audio_input: str, start_time: float, output_path: str):
    """
    Extract video segment with rotation, proper PTS reset, AND properly working audio
    """
    print(f"\nExtracting 5s segment with working audio...")
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

        # Process NEW audio - FIXED duration calculation
        print("  Processing audio...")
        video_duration = 5.0
        audio_frame_count = 0
        total_samples = 0
        target_samples = int(video_duration * input_audio.rate)  # 5s * 44100 = 220500 samples

        print(f"  Target samples: {target_samples} ({video_duration}s @ {input_audio.rate}Hz)")

        # Loop through audio until we have enough samples
        while total_samples < target_samples:
            audio_container.seek(0)  # Restart audio if needed

            for packet in audio_container.demux(audio=0):
                for frame in packet.decode():
                    if total_samples >= target_samples:
                        break

                    # Proper PTS reset for audio
                    if first_audio_pts is None:
                        first_audio_pts = frame.pts
                        print(f"    First audio PTS: {first_audio_pts}, samples: {frame.samples}")

                    # Reset PTS: start from 0, increment by samples
                    # But keep relative to first frame's original PTS
                    frame.pts = frame.pts - first_audio_pts
                    total_samples += frame.samples
                    audio_frame_count += 1

                    for encoded_packet in output_audio.encode(frame):
                        output_container.mux(encoded_packet)

                if total_samples >= target_samples:
                    break

            # Prevent infinite loop if audio file is very short
            if audio_frame_count > 1000:
                print(f"  Warning: Breaking after {audio_frame_count} frames")
                break

        actual_duration = total_samples / input_audio.rate
        print(f"  Encoded {audio_frame_count} audio frames")
        print(f"  Total samples: {total_samples} ({actual_duration:.2f}s)")

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


def verify_audio_working(path: str):
    """Verify video has audible audio"""
    print(f"\nVerifying: {path}")

    try:
        c = av.open(path)
        v = c.streams.video[0]
        a = c.streams.audio[0] if c.streams.audio else None

        # Decode frames
        video_frames = []
        for frame in c.decode(video=0):
            video_frames.append(frame.time)

        # Decode audio frames and check
        audio_frames = []
        if a:
            for frame in c.decode(audio=0):
                audio_frames.append({
                    'samples': frame.samples,
                    'time': frame.time
                })

        c.close()

        if not video_frames:
            print(f"  ✗ No video frames!")
            return False

        video_duration = video_frames[-1] - video_frames[0]

        print(f"  Resolution: {v.width}x{v.height}")
        print(f"  Video frames: {len(video_frames)}")
        print(f"  Video duration: {video_duration:.3f}s")

        if a and audio_frames:
            total_samples = sum(f['samples'] for f in audio_frames)
            audio_duration = total_samples / a.rate
            print(f"  Audio frames: {len(audio_frames)}")
            print(f"  Audio samples: {total_samples}")
            print(f"  Audio duration: {audio_duration:.3f}s")
            print(f"  Audio: {a.rate}Hz, {a.channels} channels")
        else:
            print(f"  ✗ No audio!")
            return False

        # Check criteria
        issues = []

        if len(video_frames) < 135:
            issues.append(f"Too few video frames")

        if len(audio_frames) < 10:
            issues.append(f"Too few audio frames ({len(audio_frames)}, need many more)")

        if audio_duration < 4.5:
            issues.append(f"Audio too short ({audio_duration:.2f}s, need ~5s)")

        if abs(video_duration - audio_duration) > 0.5:
            issues.append(f"Audio/video duration mismatch ({audio_duration:.2f}s vs {video_duration:.2f}s)")

        if issues:
            print(f"\n  ✗ ISSUES:")
            for issue in issues:
                print(f"    - {issue}")
            return False
        else:
            print(f"\n  ✓ ALL CHECKS PASS - Audio should be audible!")
            return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    project_root = Path(__file__).parent.parent
    input_video = project_root / "PXL_20260624_160111402.mp4"

    # Test with real music
    music_files = [
        (project_root / "music/lofi/floating_cities.mp3", "floating_cities", "Calm electronic"),
    ]

    if not Path(input_video).exists():
        print(f"Error: {input_video} not found")
        return

    # Get video duration
    container = av.open(str(input_video))
    duration = float(container.streams.video[0].duration * container.streams.video[0].time_base)
    container.close()

    print(f"Input video: {duration:.1f}s")
    start_time = duration / 2.0

    print(f"\n{'='*60}")
    print(f"Test 09: Fix Audio Duration Calculation")
    print(f"{'='*60}")

    for audio_path, style, description in music_files:
        if not Path(audio_path).exists():
            print(f"\n✗ Music not found: {audio_path}")
            continue

        output_path = project_root / f"test_outputs/09_{style}_audio_fixed.mp4"

        print(f"\n{'='*60}")
        print(f"Testing: {description}")
        print(f"{'='*60}")

        try:
            extract_with_working_audio(str(input_video), str(audio_path), start_time, str(output_path))

            if Path(output_path).exists():
                success = verify_audio_working(str(output_path))

                if success:
                    print(f"\n✓✓ SUCCESS - Audio should be clearly audible!")
                    print(f"\nPlay this file: {output_path.name}")
                    print(f"You should hear the music throughout the 5 seconds!")
                else:
                    print(f"\n✗ Still has issues - iterating...")
            else:
                print(f"\n✗ Output not created")

        except Exception as e:
            print(f"✗ Failed: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()

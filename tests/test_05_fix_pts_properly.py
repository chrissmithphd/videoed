#!/usr/bin/env python3
"""
Test 05 - Fix PTS Properly
The previous PTS reset broke duration - fix it correctly
"""

import av
import cv2
import numpy as np
from pathlib import Path


def extract_with_proper_pts_reset(input_path: str, start_time: float, output_path: str):
    """
    Extract with PROPER PTS reset that preserves duration

    Key insight: PTS must be in stream's timebase units and increment properly
    """
    print(f"Extracting 5s from {start_time:.1f}s with proper PTS handling...")

    input_container = av.open(input_path)
    output_container = av.open(output_path, 'w')

    try:
        input_video = input_container.streams.video[0]

        # Swap dimensions for 90° rotation
        output_width = input_video.height
        output_height = input_video.width

        output_video = output_container.add_stream('libx264', rate=input_video.average_rate)
        output_video.width = output_width
        output_video.height = output_height
        output_video.pix_fmt = 'yuv420p'
        output_video.options = {'crf': '18', 'preset': 'medium'}

        # Audio setup
        input_audio = None
        output_audio = None
        if input_container.streams.audio:
            input_audio = input_container.streams.audio[0]
            output_audio = output_container.add_stream(
                input_audio.codec_context.name,
                rate=input_audio.rate
            )

        end_time = start_time + 5.0
        seek_point = int(start_time * av.time_base)
        input_container.seek(seek_point)

        # Track first timestamp to calculate offset
        first_video_pts = None
        first_audio_pts = None

        frame_count = 0

        for packet in input_container.demux(video=0, audio=0 if input_audio else None):
            if packet.stream.type == 'video':
                for frame in packet.decode():
                    if frame.time < start_time:
                        continue
                    if frame.time > end_time:
                        break

                    # Apply rotation
                    img = frame.to_ndarray(format='bgr24')
                    img_rotated = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    new_frame = av.VideoFrame.from_ndarray(img_rotated, format='bgr24')

                    # PROPER PTS RESET: Store first PTS, then offset all subsequent frames
                    if first_video_pts is None:
                        first_video_pts = frame.pts
                        print(f"  First video PTS: {first_video_pts}")

                    # Reset PTS by subtracting the first frame's PTS
                    new_frame.pts = frame.pts - first_video_pts
                    new_frame.time_base = frame.time_base

                    frame_count += 1

                    for encoded_packet in output_video.encode(new_frame):
                        output_container.mux(encoded_packet)

                    if frame.time >= end_time:
                        break

            elif packet.stream.type == 'audio' and output_audio:
                for frame in packet.decode():
                    if frame.time < start_time:
                        continue
                    if frame.time > end_time:
                        break

                    # Same approach for audio
                    if first_audio_pts is None:
                        first_audio_pts = frame.pts
                        print(f"  First audio PTS: {first_audio_pts}")

                    frame.pts = frame.pts - first_audio_pts

                    for encoded_packet in output_audio.encode(frame):
                        output_container.mux(encoded_packet)

            if packet.pts and packet.pts * packet.time_base > end_time:
                break

        print(f"  Encoded {frame_count} video frames")

        # Flush
        for packet in output_video.encode(None):
            output_container.mux(packet)
        if output_audio:
            for packet in output_audio.encode(None):
                output_container.mux(packet)

        print(f"✓ Extraction complete")

    finally:
        input_container.close()
        output_container.close()


def verify_detailed(path: str):
    """Detailed verification with frame counting"""
    print(f"\nDetailed Verification: {path}")

    try:
        c = av.open(path)
        v = c.streams.video[0]
        a = c.streams.audio[0] if c.streams.audio else None

        print(f"  Resolution: {v.width}x{v.height}")
        print(f"  Video FPS: {v.average_rate}")
        print(f"  Video timebase: {v.time_base}")

        # Count and check frames
        video_frames = []
        for frame in c.decode(video=0):
            video_frames.append({
                'pts': frame.pts,
                'time': frame.time,
            })

        c.close()

        if not video_frames:
            print(f"  ✗ No frames decoded!")
            return False

        first_time = video_frames[0]['time']
        last_time = video_frames[-1]['time']
        duration = last_time - first_time

        print(f"  Video frames decoded: {len(video_frames)}")
        print(f"  First frame: PTS={video_frames[0]['pts']}, time={first_time:.3f}s")
        print(f"  Last frame: PTS={video_frames[-1]['pts']}, time={last_time:.3f}s")
        print(f"  Calculated duration: {duration:.3f}s")

        if a:
            print(f"  Audio: {a.rate}Hz, {a.channels} channels")

        # Check if duration is correct
        expected_frames = 150  # 5 seconds at 30fps
        if len(video_frames) < expected_frames * 0.9:
            print(f"  ✗ Too few frames! Expected ~{expected_frames}, got {len(video_frames)}")
            return False

        if first_time > 0.1:
            print(f"  ✗ First frame time too high: {first_time:.3f}s (should be ~0)")
            return False

        if duration < 4.5 or duration > 5.5:
            print(f"  ✗ Duration wrong: {duration:.3f}s (should be ~5s)")
            return False

        print(f"  ✓ ALL CHECKS PASS")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    input_video = "../PXL_20260624_160111402.mp4"
    output_video = "05_proper_pts_reset.mp4"

    if not Path(input_video).exists():
        print(f"Error: {input_video} not found")
        return

    # Get duration
    container = av.open(input_video)
    duration = float(container.streams.video[0].duration * container.streams.video[0].time_base)
    container.close()

    print(f"Input video duration: {duration:.1f}s")

    # Extract from middle
    start_time = duration / 2.0

    print(f"\n{'='*60}")
    print(f"Test 05: Proper PTS Reset")
    print(f"{'='*60}")

    extract_with_proper_pts_reset(input_video, start_time, output_video)

    if Path(output_video).exists():
        success = verify_detailed(output_video)

        if success:
            print(f"\n✓✓ SUCCESS - Video has correct duration and frame count!")
            print(f"\nThis is the correct PTS reset approach:")
            print(f"  1. Store first frame's PTS")
            print(f"  2. Subtract first PTS from all subsequent frames")
            print(f"  3. Keep original time_base")
        else:
            print(f"\n✗✗ FAILED - Still has issues")
    else:
        print(f"\n✗ Output file not created")


if __name__ == '__main__':
    main()

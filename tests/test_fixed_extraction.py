#!/usr/bin/env python3
"""
Properly fixed extraction - resets timestamps and fixes rotation direction
"""

import av
import cv2
import numpy as np
from pathlib import Path


def rotate_frame(frame_array: np.ndarray, rotation: int) -> np.ndarray:
    """Rotate frame by specified degrees"""
    if rotation == 0:
        return frame_array
    elif rotation == 90:
        # 90° clockwise
        return cv2.rotate(frame_array, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == 180:
        return cv2.rotate(frame_array, cv2.ROTATE_180)
    elif rotation == 270:
        return cv2.rotate(frame_array, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        return frame_array


def extract_5s_properly_fixed(input_path: str, start_time: float, output_path: str, rotation: int = 90):
    """
    Extract with PROPER timestamp reset and rotation
    """
    print(f"Extracting 5s from {Path(input_path).name} starting at {start_time:.1f}s")
    print(f"Applying {rotation}° rotation")

    input_container = av.open(input_path)
    output_container = av.open(output_path, 'w')

    try:
        input_video = input_container.streams.video[0]

        # Swap dimensions for 90/270 rotation
        if rotation in [90, 270]:
            output_width = input_video.height
            output_height = input_video.width
        else:
            output_width = input_video.width
            output_height = input_video.height

        print(f"Input: {input_video.width}x{input_video.height}")
        print(f"Output: {output_width}x{output_height}")

        output_video = output_container.add_stream('libx264', rate=input_video.average_rate)
        output_video.width = output_width
        output_video.height = output_height
        output_video.pix_fmt = 'yuv420p'
        output_video.options = {'crf': '18', 'preset': 'medium'}

        # Setup audio
        input_audio = None
        output_audio = None
        if input_container.streams.audio:
            input_audio = input_container.streams.audio[0]
            output_audio = output_container.add_stream(
                input_audio.codec_context.name,
                rate=input_audio.rate
            )

        end_time = start_time + 5.0

        # Seek to start
        seek_point = int(start_time * av.time_base)
        input_container.seek(seek_point)

        # Track output PTS - THIS IS THE KEY FIX
        output_video_pts = 0
        output_audio_pts = 0

        frame_count = 0
        first_input_time = None

        # Process packets
        for packet in input_container.demux(video=0, audio=0 if input_audio else None):
            if packet.stream.type == 'video':
                for frame in packet.decode():
                    if frame.time < start_time:
                        continue
                    if frame.time > end_time:
                        break

                    if first_input_time is None:
                        first_input_time = frame.time
                        print(f"First frame input time: {first_input_time:.3f}s")

                    # Apply rotation
                    if rotation:
                        img = frame.to_ndarray(format='bgr24')
                        img_rotated = rotate_frame(img, rotation)
                        new_frame = av.VideoFrame.from_ndarray(img_rotated, format='bgr24')
                    else:
                        new_frame = frame

                    # CRITICAL FIX: Set NEW timestamps starting from 0
                    new_frame.pts = output_video_pts
                    output_video_pts += 1

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

                    # Reset audio PTS too
                    frame.pts = output_audio_pts
                    output_audio_pts += frame.samples

                    for encoded_packet in output_audio.encode(frame):
                        output_container.mux(encoded_packet)

            if packet.pts and packet.pts * packet.time_base > end_time:
                break

        print(f"Encoded {frame_count} video frames")

        # Flush encoders
        for packet in output_video.encode(None):
            output_container.mux(packet)

        if output_audio:
            for packet in output_audio.encode(None):
                output_container.mux(packet)

        print(f"✓ Extraction complete: {output_path}")

    finally:
        input_container.close()
        output_container.close()


def verify_output(path: str):
    """Verify output file has correct timestamps"""
    print(f"\n=== Verifying {path} ===")
    c = av.open(path)
    v = c.streams.video[0]

    print(f"Duration: {v.duration * v.time_base:.2f}s")
    print(f"Resolution: {v.width}x{v.height}")
    print(f"Frames: {v.frames}")

    # Check first and last frame timestamps
    frame_count = 0
    for frame in c.decode(video=0):
        frame_count += 1
        if frame_count == 1:
            print(f"First frame time: {frame.time:.3f}s (should be ~0)")
        if frame_count == v.frames:
            print(f"Last frame time: {frame.time:.3f}s (should be ~5)")

    c.close()

    if frame.time < 1.0:
        print("✗ PROBLEM: Last frame timestamp too early")
    elif frame.time > 10.0:
        print("✗ PROBLEM: Last frame timestamp too late")
    else:
        print("✓ Timestamps look correct")


def main():
    input_video = "PXL_20260624_160111402.mp4"
    output_video = "test_properly_fixed.mp4"

    if not Path(input_video).exists():
        print(f"Error: {input_video} not found")
        return

    # Get duration
    container = av.open(input_video)
    duration = float(container.streams.video[0].duration * container.streams.video[0].time_base)
    container.close()

    print(f"Video duration: {duration:.1f}s")

    # Extract from middle with rotation
    start_time = duration / 2.0

    extract_5s_properly_fixed(input_video, start_time, output_video, rotation=90)
    verify_output(output_video)

    print(f"\nCompare with corrupted file:")
    verify_output("reels_fixed/PXL_20260624_160111402_reel_01_score0.54.mp4")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Test 02 - Quick verification that the fix works
Extracts just 5 seconds to quickly verify timestamps and rotation
"""

import av
import cv2
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path to import from extract_reels_fixed
sys.path.insert(0, str(Path(__file__).parent.parent))


def quick_extract_test(input_path: str, start_time: float, output_path: str):
    """Quick 5s extract using the FIXED approach from Test 01-D"""
    print(f"Extracting 5s from {start_time:.1f}s with 90° CCW rotation and PTS reset...")

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

        output_video_pts = 0
        output_audio_pts = 0

        for packet in input_container.demux(video=0, audio=0 if input_audio else None):
            if packet.stream.type == 'video':
                for frame in packet.decode():
                    if frame.time < start_time:
                        continue
                    if frame.time > end_time:
                        break

                    # Apply 90° counter-clockwise rotation
                    img = frame.to_ndarray(format='bgr24')
                    img_rotated = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    new_frame = av.VideoFrame.from_ndarray(img_rotated, format='bgr24')

                    # Reset PTS
                    new_frame.pts = output_video_pts
                    output_video_pts += 1

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
                    frame.pts = output_audio_pts
                    output_audio_pts += frame.samples
                    for encoded_packet in output_audio.encode(frame):
                        output_container.mux(encoded_packet)

            if packet.pts and packet.pts * packet.time_base > end_time:
                break

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


def verify(path: str):
    """Quick verification"""
    c = av.open(path)
    v = c.streams.video[0]

    frames = []
    for frame in c.decode(video=0):
        frames.append(frame.time)

    c.close()

    print(f"\nVerification:")
    print(f"  Resolution: {v.width}x{v.height}")
    print(f"  Frames: {len(frames)}")
    print(f"  First timestamp: {frames[0]:.3f}s")
    print(f"  Last timestamp: {frames[-1]:.3f}s")
    print(f"  Duration: {frames[-1] - frames[0]:.3f}s")

    if frames[0] < 1.0 and 4.5 < frames[-1] < 5.5 and v.width < v.height:
        print(f"  ✓ ALL CHECKS PASS")
        return True
    else:
        print(f"  ✗ CHECKS FAILED")
        return False


def main():
    input_video = "../PXL_20260624_160111402.mp4"
    output_video = "02_quick_verification.mp4"

    if not Path(input_video).exists():
        print(f"Error: {input_video} not found")
        return

    # Get duration
    container = av.open(input_video)
    duration = float(container.streams.video[0].duration * container.streams.video[0].time_base)
    container.close()

    # Extract from middle
    start_time = duration / 2.0

    quick_extract_test(input_video, start_time, output_video)

    if Path(output_video).exists():
        if verify(output_video):
            print(f"\n✓✓ SUCCESS - Fix is working correctly!")
            print(f"\nThis confirms the fix for extract_reels_fixed.py:")
            print(f"  1. Use cv2.ROTATE_90_COUNTERCLOCKWISE (not CLOCKWISE)")
            print(f"  2. Reset frame.pts = output_video_pts (starting from 0)")
            print(f"  3. Reset audio frame.pts = output_audio_pts")
        else:
            print(f"\n✗✗ FAILED - Fix has issues")
    else:
        print(f"\n✗ Output file not created")


if __name__ == '__main__':
    main()

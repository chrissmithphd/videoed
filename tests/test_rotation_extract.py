#!/usr/bin/env python3
"""
Test extraction WITH rotation to reproduce the corruption issue
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
        return cv2.rotate(frame_array, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == 180:
        return cv2.rotate(frame_array, cv2.ROTATE_180)
    elif rotation == 270:
        return cv2.rotate(frame_array, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        return frame_array


def extract_5s_with_rotation(input_path: str, start_time: float, output_path: str, rotation: int = 90):
    """
    Extract a 5-second segment WITH rotation applied.
    This reproduces the corruption issue from extract_reels_fixed.py
    """
    print(f"Extracting 5s from {Path(input_path).name} starting at {start_time}s")
    print(f"Applying {rotation}° rotation")

    input_container = av.open(input_path)
    output_container = av.open(output_path, 'w')

    try:
        # Setup video stream - swap dimensions for 90/270 rotation
        input_video = input_container.streams.video[0]

        if rotation in [90, 270]:
            output_width = input_video.height
            output_height = input_video.width
        else:
            output_width = input_video.width
            output_height = input_video.height

        print(f"Input resolution: {input_video.width}x{input_video.height}")
        print(f"Output resolution: {output_width}x{output_height}")

        output_video = output_container.add_stream('libx264', rate=input_video.average_rate)
        output_video.width = output_width
        output_video.height = output_height
        output_video.pix_fmt = 'yuv420p'
        output_video.options = {'crf': '18', 'preset': 'medium'}

        # Setup audio stream
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

        frame_count = 0

        # Process packets
        for packet in input_container.demux(video=0, audio=0 if input_audio else None):
            if packet.stream.type == 'video':
                for frame in packet.decode():
                    if frame.time < start_time:
                        continue
                    if frame.time > end_time:
                        break

                    # THIS IS THE PROBLEMATIC CODE - applying rotation
                    if rotation:
                        # Convert to numpy array
                        img = frame.to_ndarray(format='bgr24')
                        # Rotate the image
                        img_rotated = rotate_frame(img, rotation)
                        # Create new frame from rotated image
                        new_frame = av.VideoFrame.from_ndarray(img_rotated, format='bgr24')
                        new_frame.pts = frame.pts
                        new_frame.time_base = frame.time_base
                        frame = new_frame

                    # Encode the (possibly rotated) frame
                    for encoded_packet in output_video.encode(frame):
                        output_container.mux(encoded_packet)

                    frame_count += 1

                    if frame.time >= end_time:
                        break

            elif packet.stream.type == 'audio' and output_audio:
                for frame in packet.decode():
                    if frame.time < start_time:
                        continue
                    if frame.time > end_time:
                        break

                    for encoded_packet in output_audio.encode(frame):
                        output_container.mux(encoded_packet)

            # Stop if we're past the end time
            if packet.pts and packet.pts * packet.time_base > end_time:
                break

        print(f"Encoded {frame_count} frames")

        # Flush encoders
        print("Flushing video encoder...")
        for packet in output_video.encode(None):
            output_container.mux(packet)

        if output_audio:
            print("Flushing audio encoder...")
            for packet in output_audio.encode(None):
                output_container.mux(packet)

        print(f"✓ Extraction complete: {output_path}")

    except Exception as e:
        print(f"✗ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input_container.close()
        output_container.close()


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds"""
    container = av.open(video_path)
    try:
        video_stream = container.streams.video[0]
        duration = float(video_stream.duration * video_stream.time_base)
        return duration
    finally:
        container.close()


def main():
    input_video = "PXL_20260624_160111402.mp4"
    output_video = "test_5s_rotated.mp4"

    if not Path(input_video).exists():
        print(f"Error: {input_video} not found")
        return

    duration = get_video_duration(input_video)
    print(f"Video duration: {duration:.1f}s")

    # Extract from middle of video with 90° rotation
    start_time = duration / 2.0

    print(f"\nExtracting 5 seconds with 90° rotation starting at {start_time:.1f}s...")
    extract_5s_with_rotation(input_video, start_time, output_video, rotation=90)

    # Check output file
    output_path = Path(output_video)
    if output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ File created!")
        print(f"  Output file: {output_video}")
        print(f"  File size: {size_mb:.2f} MB")

        # Try to verify it's readable
        print(f"\nVerifying video integrity...")
        try:
            container = av.open(output_video)
            video_stream = container.streams.video[0]
            print(f"  Duration: {video_stream.duration * video_stream.time_base:.2f}s")
            print(f"  Frames: {video_stream.frames}")
            print(f"  Codec: {video_stream.codec_context.name}")
            print(f"  Resolution: {video_stream.width}x{video_stream.height}")

            # Try to read first frame
            for frame in container.decode(video=0):
                print(f"  ✓ First frame readable: {frame.width}x{frame.height}")
                break

            container.close()
            print(f"\n✓✓ SUCCESS - Video is valid and playable!")
        except Exception as e:
            print(f"\n✗✗ CORRUPTION DETECTED - Video cannot be read: {e}")
    else:
        print(f"\n✗ Failed - output file not created")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Minimal video extraction test - extract 5 seconds without any rotation or complex features
"""

import av
from pathlib import Path


def extract_5s_segment(input_path: str, start_time: float, output_path: str):
    """
    Extract a simple 5-second segment using PyAV with minimal code.
    No rotation, no complex features - just basic extraction.
    """
    print(f"Extracting 5s from {Path(input_path).name} starting at {start_time}s")

    input_container = av.open(input_path)
    output_container = av.open(output_path, 'w')

    try:
        # Setup video stream
        input_video = input_container.streams.video[0]
        output_video = output_container.add_stream('libx264', rate=input_video.average_rate)
        output_video.width = input_video.width
        output_video.height = input_video.height
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

        # Process packets
        for packet in input_container.demux(video=0, audio=0 if input_audio else None):
            if packet.stream.type == 'video':
                for frame in packet.decode():
                    if frame.time < start_time:
                        continue
                    if frame.time > end_time:
                        break

                    # Encode frame as-is (no modifications)
                    for encoded_packet in output_video.encode(frame):
                        output_container.mux(encoded_packet)

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
    # Use the first test video
    input_video = "PXL_20260624_160111402.mp4"
    output_video = "test_5s_extract.mp4"

    if not Path(input_video).exists():
        print(f"Error: {input_video} not found")
        return

    # Get duration and extract from middle
    duration = get_video_duration(input_video)
    print(f"Video duration: {duration:.1f}s")

    # Extract from middle of video
    start_time = duration / 2.0

    print(f"\nExtracting 5 seconds starting at {start_time:.1f}s...")
    extract_5s_segment(input_video, start_time, output_video)

    # Check output file
    output_path = Path(output_video)
    if output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ Success!")
        print(f"  Output file: {output_video}")
        print(f"  File size: {size_mb:.2f} MB")
        print(f"\nTo verify the video plays correctly:")
        print(f"  ffplay {output_video}")
        print(f"  # or")
        print(f"  ffprobe {output_video}")
    else:
        print(f"\n✗ Failed - output file not created")


if __name__ == '__main__':
    main()

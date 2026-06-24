#!/usr/bin/env python3
"""
Test 11 - Final Working Audio Solution
Fix: Properly loop audio by re-opening container each time
"""

import av
import cv2
import numpy as np
from pathlib import Path


def extract_final_working(video_input: str, audio_input: str, start_time: float, output_path: str):
    """Final working version with proper audio looping"""

    video_container = av.open(video_input)
    output_container = av.open(output_path, 'w')

    try:
        input_video = video_container.streams.video[0]

        # Video setup with rotation
        output_video = output_container.add_stream('libx264', rate=input_video.average_rate)
        output_video.width = input_video.height  # Swap for rotation
        output_video.height = input_video.width
        output_video.pix_fmt = 'yuv420p'
        output_video.options = {'crf': '18', 'preset': 'medium'}

        # Audio setup
        output_audio = output_container.add_stream('aac', rate=44100)

        end_time = start_time + 5.0
        video_container.seek(int(start_time * av.time_base))

        first_video_pts = None
        video_frame_count = 0

        # Process video
        for packet in video_container.demux(video=0):
            for frame in packet.decode():
                if frame.time < start_time or frame.time > end_time:
                    continue

                original_pts = frame.pts
                if first_video_pts is None:
                    first_video_pts = original_pts

                # Rotate and reset PTS
                img = cv2.rotate(frame.to_ndarray(format='bgr24'), cv2.ROTATE_90_COUNTERCLOCKWISE)
                new_frame = av.VideoFrame.from_ndarray(img, format='bgr24')
                new_frame.pts = original_pts - first_video_pts
                new_frame.time_base = frame.time_base
                video_frame_count += 1

                for pkt in output_video.encode(new_frame):
                    output_container.mux(pkt)

        print(f"Video: {video_frame_count} frames")

        # Process audio - COLLECT ALL FRAMES FIRST, then encode
        target_samples = int(5.0 * 44100)
        audio_frames_list = []
        total_samples = 0

        # Read audio frames until we have enough
        audio_container = av.open(audio_input)
        while total_samples < target_samples:
            audio_container.seek(0)
            for packet in audio_container.demux(audio=0):
                for frame in packet.decode():
                    if total_samples >= target_samples:
                        break
                    audio_frames_list.append(frame)
                    total_samples += frame.samples
                if total_samples >= target_samples:
                    break
        audio_container.close()

        # Now encode collected frames with proper PTS
        audio_pts = 0
        for frame in audio_frames_list:
            frame.pts = audio_pts
            audio_pts += frame.samples
            for pkt in output_audio.encode(frame):
                output_container.mux(pkt)

        print(f"Audio: {len(audio_frames_list)} frames, {total_samples} samples")

        # Flush
        for pkt in output_video.encode(None):
            output_container.mux(pkt)
        for pkt in output_audio.encode(None):
            output_container.mux(pkt)

    finally:
        video_container.close()
        output_container.close()


def main():
    project_root = Path(__file__).parent.parent
    input_video = project_root / "PXL_20260624_160111402.mp4"
    audio_file = project_root / "music/lofi/floating_cities.mp3"
    output_path = project_root / "test_outputs/11_final_working.mp4"

    # Get start time
    c = av.open(str(input_video))
    duration = float(c.streams.video[0].duration * c.streams.video[0].time_base)
    c.close()
    start_time = duration / 2.0

    print("Test 11: Final Working Audio")
    print(f"Extracting 5s @ {start_time:.1f}s...")

    extract_final_working(str(input_video), str(audio_file), start_time, str(output_path))

    # Verify
    c = av.open(str(output_path))
    v = c.streams.video[0]
    a = c.streams.audio[0]
    audio_frames = list(c.decode(audio=0))
    audio_duration = sum(f.samples for f in audio_frames) / a.rate
    c.close()

    print(f"\n✓ Created: {output_path.name}")
    print(f"  Video: {v.width}x{v.height}")
    print(f"  Audio: {len(audio_frames)} frames, {audio_duration:.2f}s")
    print(f"\n{'✓✓ PASS' if audio_duration > 4.5 else '✗ FAIL'}")


if __name__ == '__main__':
    main()

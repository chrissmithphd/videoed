#!/usr/bin/env python3
"""
Test 01 - Comprehensive Video Extraction Debug
Tests multiple approaches with clear numbered outputs and detailed verification
"""

import av
import cv2
import numpy as np
from pathlib import Path


def verify_video(path: str, test_name: str):
    """Verify video and print detailed diagnostics"""
    print(f"\n{'='*60}")
    print(f"Verifying: {test_name}")
    print(f"File: {path}")
    print(f"{'='*60}")

    try:
        c = av.open(path)
        v = c.streams.video[0]

        # Get metadata
        duration = v.duration * v.time_base if v.duration else 0
        print(f"Resolution: {v.width}x{v.height}")
        print(f"Reported duration: {duration:.2f}s")
        print(f"Reported frames: {v.frames}")
        print(f"FPS: {v.average_rate}")

        # Decode all frames and check timestamps
        frames = []
        for frame in c.decode(video=0):
            frames.append({
                'time': frame.time,
                'pts': frame.pts,
                'width': frame.width,
                'height': frame.height
            })

        c.close()

        if not frames:
            print("✗ ERROR: No frames decoded!")
            return False

        first_time = frames[0]['time']
        last_time = frames[-1]['time']
        actual_duration = last_time - first_time

        print(f"Actual frames decoded: {len(frames)}")
        print(f"First frame timestamp: {first_time:.3f}s")
        print(f"Last frame timestamp: {last_time:.3f}s")
        print(f"Actual duration: {actual_duration:.3f}s")

        # Check for issues
        issues = []

        # Issue 1: Timestamps don't start near zero
        if first_time > 1.0:
            issues.append(f"Timestamps don't start at 0 (start={first_time:.1f}s)")

        # Issue 2: Duration mismatch
        if abs(actual_duration - 5.0) > 0.5:
            issues.append(f"Duration not ~5s (actual={actual_duration:.1f}s)")

        # Issue 3: Check rotation (portrait should be taller than wide)
        if frames[0]['width'] > frames[0]['height']:
            issues.append(f"Video is landscape ({frames[0]['width']}x{frames[0]['height']}) - should be portrait")

        if issues:
            print("\n✗ ISSUES FOUND:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("\n✓ ALL CHECKS PASSED")
            return True

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def extract_no_rotation_no_pts_fix(input_path: str, start_time: float, output_path: str):
    """Test 01-A: No rotation, no PTS fix (baseline)"""
    print(f"\n>>> Test 01-A: Baseline (no rotation, no PTS fix)")

    input_container = av.open(input_path)
    output_container = av.open(output_path, 'w')

    try:
        input_video = input_container.streams.video[0]
        output_video = output_container.add_stream('libx264', rate=input_video.average_rate)
        output_video.width = input_video.width
        output_video.height = input_video.height
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

        for packet in input_container.demux(video=0, audio=0 if input_audio else None):
            if packet.stream.type == 'video':
                for frame in packet.decode():
                    if frame.time < start_time:
                        continue
                    if frame.time > end_time:
                        break

                    # No modifications - just encode as-is
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

            if packet.pts and packet.pts * packet.time_base > end_time:
                break

        # Flush
        for packet in output_video.encode(None):
            output_container.mux(packet)
        if output_audio:
            for packet in output_audio.encode(None):
                output_container.mux(packet)

    finally:
        input_container.close()
        output_container.close()

    print(f"✓ Written: {output_path}")


def extract_with_pts_fix_no_rotation(input_path: str, start_time: float, output_path: str):
    """Test 01-B: PTS fix, no rotation"""
    print(f"\n>>> Test 01-B: With PTS fix, no rotation")

    input_container = av.open(input_path)
    output_container = av.open(output_path, 'w')

    try:
        input_video = input_container.streams.video[0]
        output_video = output_container.add_stream('libx264', rate=input_video.average_rate)
        output_video.width = input_video.width
        output_video.height = input_video.height
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

                    # PTS FIX: Reset to start from 0
                    frame.pts = output_video_pts
                    output_video_pts += 1

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

                    # Reset audio PTS
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

    finally:
        input_container.close()
        output_container.close()

    print(f"✓ Written: {output_path}")


def extract_with_rotation_90cw_and_pts_fix(input_path: str, start_time: float, output_path: str):
    """Test 01-C: 90° clockwise rotation + PTS fix"""
    print(f"\n>>> Test 01-C: 90° clockwise rotation + PTS fix")

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

                    # Apply 90° clockwise rotation
                    img = frame.to_ndarray(format='bgr24')
                    img_rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                    new_frame = av.VideoFrame.from_ndarray(img_rotated, format='bgr24')

                    # PTS FIX
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

    finally:
        input_container.close()
        output_container.close()

    print(f"✓ Written: {output_path}")


def extract_with_rotation_90ccw_and_pts_fix(input_path: str, start_time: float, output_path: str):
    """Test 01-D: 90° counter-clockwise rotation + PTS fix"""
    print(f"\n>>> Test 01-D: 90° counter-clockwise rotation + PTS fix")

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

                    # PTS FIX
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

    finally:
        input_container.close()
        output_container.close()

    print(f"✓ Written: {output_path}")


def main():
    input_video = "../PXL_20260624_160111402.mp4"

    if not Path(input_video).exists():
        print(f"Error: {input_video} not found")
        return

    # Get video info
    container = av.open(input_video)
    v = container.streams.video[0]
    duration = float(v.duration * v.time_base)
    print(f"Input video: {v.width}x{v.height}, {duration:.1f}s")
    container.close()

    # Extract from middle
    start_time = duration / 2.0

    print(f"\n{'#'*60}")
    print(f"# Running 4 extraction tests")
    print(f"# Start time: {start_time:.1f}s")
    print(f"# Duration: 5s")
    print(f"{'#'*60}")

    # Run all tests
    tests = [
        ("01-A_no_rotation_no_pts_fix.mp4", extract_no_rotation_no_pts_fix),
        ("01-B_pts_fix_no_rotation.mp4", extract_with_pts_fix_no_rotation),
        ("01-C_rotation_90cw_with_pts_fix.mp4", extract_with_rotation_90cw_and_pts_fix),
        ("01-D_rotation_90ccw_with_pts_fix.mp4", extract_with_rotation_90ccw_and_pts_fix),
    ]

    for output_name, extract_func in tests:
        output_path = output_name
        try:
            extract_func(input_video, start_time, output_path)
        except Exception as e:
            print(f"✗ Test failed: {e}")
            import traceback
            traceback.print_exc()

    # Verify all outputs
    print(f"\n\n{'#'*60}")
    print(f"# Verification Results")
    print(f"{'#'*60}")

    results = []
    for output_name, _ in tests:
        if Path(output_name).exists():
            passed = verify_video(output_name, output_name)
            results.append((output_name, passed))
        else:
            print(f"\n✗ {output_name} - FILE NOT CREATED")
            results.append((output_name, False))

    # Summary
    print(f"\n\n{'#'*60}")
    print(f"# SUMMARY")
    print(f"{'#'*60}")
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")

    print(f"\nAll test outputs are in: test_outputs/")
    print(f"\nExpected results:")
    print(f"  01-A: FAIL (no PTS fix, landscape)")
    print(f"  01-B: PASS (PTS fixed, landscape)")
    print(f"  01-C: PASS or FAIL (PTS fixed, portrait - check if right-side-up)")
    print(f"  01-D: PASS or FAIL (PTS fixed, portrait - check if right-side-up)")
    print(f"\nPlay the 01-C and 01-D files to see which rotation direction is correct!")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Test 08 - Audio Replacement with REAL Music
Use actual lofi tracks instead of synthesized tones
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Import the working extraction function from test_06
from test_06_audio_replacement_fixed import extract_and_replace_audio, verify_complete


def main():
    # Paths relative to project root
    project_root = Path(__file__).parent.parent
    input_video = project_root / "PXL_20260624_160111402.mp4"

    # Use REAL music tracks
    music_files = [
        (project_root / "music/lofi/floating_cities.mp3", "floating_cities", "Calm electronic by Kevin MacLeod"),
        (project_root / "music/lofi/long_note_two.mp3", "long_note_two", "Minimal ambient by Kevin MacLeod"),
    ]

    if not Path(input_video).exists():
        print(f"Error: {input_video} not found")
        return

    # Get video duration
    import av
    container = av.open(input_video)
    duration = float(container.streams.video[0].duration * container.streams.video[0].time_base)
    container.close()

    print(f"Input video: {duration:.1f}s")
    start_time = duration / 2.0

    print(f"\n{'='*60}")
    print(f"Test 08: Real Music Replacement")
    print(f"{'='*60}")

    results = []

    for audio_path, style, description in music_files:
        if not Path(audio_path).exists():
            print(f"\n✗ Music not found: {audio_path}")
            print("Run test_07_download_real_music.py first")
            continue

        output_path = project_root / f"test_outputs/08_{style}_real_music.mp4"

        print(f"\n{'='*60}")
        print(f"Testing: {description}")
        print(f"{'='*60}")

        try:
            extract_and_replace_audio(input_video, audio_path, start_time, output_path)

            if Path(output_path).exists():
                success = verify_complete(output_path)
                results.append((style, output_path, success, description))
            else:
                results.append((style, output_path, False, description))
        except Exception as e:
            print(f"✗ Failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((style, output_path, False, description))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY - REAL MUSIC TESTS")
    print(f"{'='*60}")

    for style, path, success, description in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {Path(path).name}")
        print(f"       {description}")

    if any(success for _, _, success, _ in results):
        print(f"\n✓✓ Real music replacement working!")
        print(f"\nThese videos have ACTUAL music, not synthesized tones.")
        print(f"\nAttribution required in video description:")
        print(f"  'Music by Kevin MacLeod (incompetech.com)'")
        print(f"  License: CC-BY 4.0")
        print(f"\nFiles to review:")
        for style, path, success, description in results:
            if success:
                print(f"  - {Path(path).name}")
    else:
        print(f"\n✗✗ All tests failed")


if __name__ == '__main__':
    main()

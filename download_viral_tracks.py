#!/usr/bin/env python3
"""
Download 5 viral-ready tracks from Freesound.org
These are the tracks found by the research agent.
"""
import requests
from pathlib import Path

# Track metadata with direct download attempts
TRACKS = [
    {
        "name": "01_uplifting_presentations_viramiller.mp3",
        "url": "https://cdn.freesound.org/previews/746/746677_16085323-hq.mp3",
        "artist": "ViraMiller",
        "freesound_id": 746677
    },
    {
        "name": "02_90s_smooth_funk_yellowtree.mp3",
        "url": "https://cdn.freesound.org/previews/621/621091_1954411-hq.mp3",
        "artist": "YellowTree",
        "freesound_id": 621091
    },
    {
        "name": "03_cheerful_happy_universfield.mp3",
        "url": "https://cdn.freesound.org/previews/769/769380_16024318-hq.mp3",
        "artist": "Gustavo_Alivera",
        "freesound_id": 769380
    },
    {
        "name": "04_happy_orchestra_loop_migfus20.mp3",
        "url": "https://cdn.freesound.org/previews/561/561383_12295155-hq.mp3",
        "artist": "Migfus20",
        "freesound_id": 561383
    },
    {
        "name": "05_vibrant_uplifting_matio888.mp3",
        "url": "https://cdn.freesound.org/previews/789/789329_16936704-hq.mp3",
        "artist": "Matio888",
        "freesound_id": 789329
    }
]

output_dir = Path("music/viral")
output_dir.mkdir(parents=True, exist_ok=True)

print("Downloading 5 viral-ready tracks from Freesound.org...")
print("=" * 80)

success_count = 0

for track in TRACKS:
    output_path = output_dir / track["name"]

    try:
        print(f"\n📥 Downloading: {track['name']}")
        print(f"   Artist: {track['artist']}")

        # Try direct CDN download
        response = requests.get(track["url"], timeout=30, allow_redirects=True)
        response.raise_for_status()

        # Check if we got actual audio data (not an error page)
        if len(response.content) > 1000 and response.headers.get('content-type', '').startswith('audio'):
            output_path.write_bytes(response.content)
            size_kb = len(response.content) / 1024
            print(f"   ✓ Downloaded: {size_kb:.1f} KB")
            success_count += 1
        else:
            print(f"   ✗ Failed: Got {len(response.content)} bytes (not audio)")
            print(f"   ℹ Manual download: https://freesound.org/people/{track['artist']}/sounds/{track['freesound_id']}/")

    except Exception as e:
        print(f"   ✗ Error: {e}")
        print(f"   ℹ Manual download: https://freesound.org/people/{track['artist']}/sounds/{track['freesound_id']}/")

print("\n" + "=" * 80)
print(f"\n✓ Downloaded {success_count}/5 tracks successfully!")

if success_count < 5:
    print("\n⚠ Some tracks failed to download automatically.")
    print("You can download them manually from Freesound.org:")
    print("  1. Visit the URLs shown above")
    print("  2. Click 'Download' button (requires free account)")
    print("  3. Save to: music/viral/")
    print("\nNote: Preview URLs may require authentication or have rate limits.")

print("\nAll tracks are CC-BY licensed - attribution required:")
print("  'Music by [Artist] / freesound.org'")

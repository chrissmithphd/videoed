#!/usr/bin/env python3
"""
Test 12 - Download Viral-Ready Music
Get upbeat tracks suitable for social media reels (80-120 BPM)
"""

import urllib.request
from pathlib import Path


def download_viral_tracks():
    """
    Download upbeat, energetic tracks suitable for viral reels
    Focus on 80-120 BPM, shorter tracks (2-3 min), catchy melodies
    """
    music_dir = Path("../music/viral")
    music_dir.mkdir(parents=True, exist_ok=True)

    # Incompetech upbeat tracks (CC-BY 4.0)
    tracks = [
        {
            "name": "Wallpaper",
            "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Wallpaper.mp3",
            "desc": "Upbeat electronic, 120 BPM, energetic",
            "bpm": 120
        },
        {
            "name": "Sneaky Snitch",
            "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Sneaky%20Snitch.mp3",
            "desc": "Playful, quirky, very popular on TikTok",
            "bpm": 120
        },
        {
            "name": "Cipher",
            "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Cipher.mp3",
            "desc": "Mysterious, engaging, good for suspense",
            "bpm": 85
        },
        {
            "name": "Fluffing a Duck",
            "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Fluffing%20a%20Duck.mp3",
            "desc": "Happy, upbeat acoustic, feel-good vibes",
            "bpm": 90
        },
    ]

    print("=" * 60)
    print("Test 12: Downloading Viral-Ready Music")
    print("=" * 60)
    print()
    print("Target: Upbeat tracks (80-120 BPM) for viral social media reels")
    print()

    downloaded = []
    for track in tracks:
        output_path = music_dir / f"{track['name'].lower().replace(' ', '_')}.mp3"

        print(f"Downloading: {track['name']}")
        print(f"  {track['desc']}")
        print(f"  BPM: {track['bpm']}")

        try:
            urllib.request.urlretrieve(track['url'], str(output_path))
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ Downloaded: {size_mb:.1f} MB")
            downloaded.append(track['name'])
        except Exception as e:
            print(f"  ✗ Failed: {e}")

        print()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if downloaded:
        print(f"✓ Downloaded {len(downloaded)}/{len(tracks)} tracks")
        print()
        print("These are UPBEAT, viral-ready tracks!")
        print()
        print("Attribution required:")
        print("  'Music by Kevin MacLeod (incompetech.com)'")
        print("  License: CC-BY 4.0")
        print()
        print("Tracks downloaded:")
        for name in downloaded:
            print(f"  - {name}")
    else:
        print("✗ No tracks downloaded")

    print()
    print("RECOMMENDATIONS FOR VIRAL REELS:")
    print("  1. 'Sneaky Snitch' - Most popular, quirky/fun")
    print("  2. 'Fluffing a Duck' - Feel-good, upbeat")
    print("  3. 'Wallpaper' - High energy, electronic")
    print()
    print("These tracks are SHORT, CATCHY, and UPBEAT - perfect for reels!")


if __name__ == '__main__':
    download_viral_tracks()

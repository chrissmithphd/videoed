#!/usr/bin/env python3
"""
Test 07 - Download Real Lofi Music
Download actual lofi/chill music from free sources for viral-ready reels
"""

import urllib.request
import json
from pathlib import Path


def download_pixabay_music():
    """
    Download lofi/chill music from Pixabay (no attribution required)

    Note: Pixabay requires API key for programmatic access
    For manual testing, go to: https://pixabay.com/music/search/lofi/
    """
    print("Pixabay Music:")
    print("  Website: https://pixabay.com/music/search/lofi/")
    print("  License: Free, no attribution required")
    print("  Manual download needed (no API key configured)")
    print()
    print("Recommended tracks:")
    print("  1. 'Lofi Study' - Chill beats, 2-3 min")
    print("  2. 'Lofi Chill' - Relaxed vibe, perfect for reels")
    print("  3. 'Chill Lofi Hip Hop' - Popular style")
    print()


def download_bensound_tracks():
    """
    List Bensound lofi/chill tracks for manual download
    """
    print("Bensound - Hand-picked lofi/chill tracks:")
    print("  Website: https://www.bensound.com")
    print("  License: Free for YouTube/social media")
    print()

    # Recommended tracks from Bensound
    tracks = [
        {
            "name": "Cute",
            "url": "https://www.bensound.com/royalty-free-music/track/cute",
            "description": "Light, upbeat, perfect for feel-good content",
            "duration": "3:14"
        },
        {
            "name": "Little Idea",
            "url": "https://www.bensound.com/royalty-free-music/track/little-idea",
            "description": "Playful, quirky, great for creative content",
            "duration": "2:15"
        },
        {
            "name": "Relaxing",
            "url": "https://www.bensound.com/royalty-free-music/track/relaxing",
            "description": "Calm acoustic, perfect for nature/travel",
            "duration": "3:49"
        },
        {
            "name": "Memories",
            "url": "https://www.bensound.com/royalty-free-music/track/memories",
            "description": "Emotional piano, storytelling vibes",
            "duration": "3:30"
        }
    ]

    for track in tracks:
        print(f"  • {track['name']} ({track['duration']})")
        print(f"    {track['description']}")
        print(f"    {track['url']}")
        print()


def download_incompetech_lofi():
    """
    List Kevin MacLeod (Incompetech) lofi/chill tracks
    """
    print("Incompetech (Kevin MacLeod) - CC-BY License:")
    print("  Website: https://incompetech.com/music/royalty-free/music.html")
    print("  License: CC-BY 4.0 (requires attribution)")
    print("  Attribution: 'Music by Kevin MacLeod (incompetech.com)'")
    print()

    tracks = [
        {
            "name": "Airship Intro",
            "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Airship%20Intro.mp3",
            "description": "Dreamy, ethereal, great for chill content",
            "genre": "Ambient"
        },
        {
            "name": "Floating Cities",
            "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Floating%20Cities.mp3",
            "description": "Calm electronic, perfect for tech/urban",
            "genre": "Electronic"
        },
        {
            "name": "Long Note Two",
            "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Long%20Note%20Two.mp3",
            "description": "Minimal ambient, very chill",
            "genre": "Ambient"
        }
    ]

    print("  Recommended tracks (can download directly):")
    for track in tracks:
        print(f"  • {track['name']} - {track['genre']}")
        print(f"    {track['description']}")
        print(f"    Download: {track['url']}")
        print()


def download_track(url: str, output_path: str):
    """Download a track from URL"""
    try:
        print(f"Downloading: {url}")
        urllib.request.urlretrieve(url, output_path)
        size_kb = Path(output_path).stat().st_size / 1024
        print(f"  ✓ Downloaded: {output_path} ({size_kb:.1f} KB)")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    music_dir = Path("../music/lofi")
    music_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Test 07: Real Lofi/Chill Music for Viral Reels")
    print("=" * 60)
    print()

    # Show all sources
    download_pixabay_music()
    print("-" * 60)
    print()

    download_bensound_tracks()
    print("-" * 60)
    print()

    download_incompetech_lofi()
    print("-" * 60)
    print()

    # Try to download Incompetech tracks (direct download available)
    print("Attempting to download Incompetech tracks...")
    print()

    incompetech_tracks = [
        ("Airship Intro", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Airship%20Intro.mp3"),
        ("Floating Cities", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Floating%20Cities.mp3"),
        ("Long Note Two", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Long%20Note%20Two.mp3"),
    ]

    downloaded = []
    for name, url in incompetech_tracks:
        output_path = music_dir / f"{name.lower().replace(' ', '_')}.mp3"
        if download_track(url, str(output_path)):
            downloaded.append(output_path.name)
        print()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if downloaded:
        print(f"✓ Downloaded {len(downloaded)} tracks to: {music_dir}/")
        for track in downloaded:
            print(f"  - {track}")
        print()
        print("These are REAL music tracks, not synthesized tones!")
        print()
        print("Attribution required:")
        print("  'Music by Kevin MacLeod (incompetech.com)'")
        print("  License: CC-BY 4.0")
    else:
        print("✗ No tracks downloaded automatically")

    print()
    print("MANUAL DOWNLOAD RECOMMENDATIONS:")
    print()
    print("For best viral potential, manually download from:")
    print("  1. Bensound 'Cute' - Upbeat, feel-good")
    print("  2. Pixabay 'Lofi Chill' - Popular lofi style")
    print("  3. Incompetech 'Floating Cities' - Calm electronic")
    print()
    print("Save to: music/lofi/")


if __name__ == '__main__':
    main()

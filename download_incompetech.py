#!/usr/bin/env python3
"""
Download professional royalty-free music from Kevin MacLeod (Incompetech)
CC-BY 4.0 licensed - requires attribution but sounds professional
"""
import requests
from pathlib import Path
import time

TRACKS = [
    {
        "name": "Happy_Alley.mp3",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Happy%20Alley.mp3",
        "description": "Upbeat rock, 112 BPM, 1:20",
        "credit": "Happy Alley by Kevin MacLeod"
    },
    {
        "name": "Funky_One.mp3",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Funky%20One.mp3",
        "description": "Groovy funk, 3:00",
        "credit": "Funky One by Kevin MacLeod"
    },
    {
        "name": "Go_Cart.mp3",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Go%20Cart.mp3",
        "description": "Energetic electronic, 115 BPM, 3:33",
        "credit": "Go Cart by Kevin MacLeod"
    },
]

output_dir = Path("music/viral")
output_dir.mkdir(parents=True, exist_ok=True)

print("Downloading professional tracks from Incompetech...")
print("=" * 70)

success = 0
for track in TRACKS:
    output_path = output_dir / track["name"]
    
    try:
        print(f"\n📥 {track['description']}")
        
        response = requests.get(track["url"], timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        if len(response.content) > 100000:  # At least 100KB
            output_path.write_bytes(response.content)
            size_mb = len(response.content) / 1024 / 1024
            print(f"   ✓ {track['name']} ({size_mb:.1f} MB)")
            print(f"   Credit: \"{track['credit']}\"")
            success += 1
        else:
            print(f"   ✗ Download failed (too small: {len(response.content)} bytes)")
            
        time.sleep(1)  # Be nice to the server
        
    except Exception as e:
        print(f"   ✗ Error: {e}")

print("\n" + "=" * 70)
print(f"✓ Downloaded {success}/{len(TRACKS)} tracks")
print("\nAttribution required (add to video description):")
print("  Music by Kevin MacLeod (incompetech.com)")
print("  Licensed under Creative Commons: By Attribution 4.0")
print("  http://creativecommons.org/licenses/by/4.0/")

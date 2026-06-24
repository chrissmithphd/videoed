#!/usr/bin/env python3
"""
Quick audio search using Freesound API
Usage: python search_music.py "upbeat electronic floating cities"
"""
import sys
import requests

# Free API key for testing (replace with your own from https://freesound.org/api/apply/)
API_KEY = "YOUR_KEY_HERE"

def search_freesound(query, exclude_tags=None):
    """Search Freesound for music"""
    exclude_tags = exclude_tags or ["dark", "horror", "drone", "scary"]
    
    # Build filter
    exclude_filter = " ".join([f'-tag:{tag}' for tag in exclude_tags])
    filter_str = f'license:"Creative Commons 0" duration:[15 TO 120] {exclude_filter}'
    
    url = "https://freesound.org/apiv2/search/text/"
    params = {
        "query": query,
        "token": API_KEY,
        "fields": "id,name,previews,license,duration,tags,username",
        "filter": filter_str,
        "sort": "rating_desc",
        "page_size": 10
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        
        results = resp.json().get("results", [])
        
        print(f"\nFound {len(results)} tracks for: '{query}'\n")
        print("=" * 80)
        
        for i, track in enumerate(results, 1):
            print(f"\n{i}. {track['name']}")
            print(f"   Artist: {track.get('username', 'Unknown')}")
            print(f"   Duration: {track.get('duration', 0):.1f}s")
            print(f"   License: {track.get('license', 'Unknown')}")
            
            # Preview URLs
            previews = track.get('previews', {})
            if 'preview-hq-mp3' in previews:
                print(f"   Preview: {previews['preview-hq-mp3']}")
            
            # Tags (first 5)
            tags = track.get('tags', [])
            if tags:
                print(f"   Tags: {', '.join(tags[:5])}")
            
            # Freesound URL
            print(f"   URL: https://freesound.org/people/{track.get('username')}/sounds/{track['id']}/")
        
        print("\n" + "=" * 80)
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        print("\nNote: Get your free API key at https://freesound.org/api/apply/")
        print("Then set: API_KEY = 'your_key_here' in this script")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_music.py 'search query'")
        print("Example: python search_music.py 'upbeat electronic floating cities'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    search_freesound(query)

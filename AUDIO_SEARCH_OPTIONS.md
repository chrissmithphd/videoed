# Audio Search Services & MCPs for VideoReel Generator

**Date:** 2026-06-24  
**Purpose:** Find viral-ready background music by text description for 5-20 second video clips

---

## MCP SERVERS FOR AUDIO SEARCH

### 1. Freesound MCP Server (Recommended)
**Repository:** https://github.com/johnkimdw/freesound-mcp-server  
**Stars:** 5 (most popular Freesound MCP)  
**Language:** Python  
**Last Updated:** 2026-03-28

#### Features
- Search audio by natural language ("upbeat electronic", "energetic acoustic")
- Access 300,000+ Creative Commons licensed sounds
- Filter by duration, tags, license type
- Get preview URLs (high and low quality)
- Retrieve detailed metadata (duration, tags, licensing)

#### Installation (Docker - Recommended)
```bash
# Clone and build
git clone https://github.com/johnkimdw/freesound-mcp-server.git
cd freesound-mcp-server
docker build -t freesound-mcp .

# Get API key from: https://freesound.org/api/apply/
```

#### Claude Desktop Configuration
Add to `~/.claude/settings.json` (Linux) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "freesound": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "FREESOUND_API_KEY",
        "freesound-mcp"
      ],
      "env": {
        "FREESOUND_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

#### Claude Code Configuration
```bash
# From the freesound-mcp-server directory
claude mcp add freesound -e FREESOUND_API_KEY=your-api-key-here -- docker run -i --rm -e FREESOUND_API_KEY freesound-mcp
```

#### Local Installation (Alternative)
```bash
# Requires Python 3.10+ and uv package manager
git clone https://github.com/johnkimdw/freesound-mcp-server.git
cd freesound-mcp-server
uv sync
export FREESOUND_API_KEY=your_api_key_here

# Claude Desktop config:
{
  "mcpServers": {
    "freesound": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/freesound-mcp-server",
        "run",
        "freesound-mcp"
      ],
      "env": {
        "FREESOUND_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

#### Usage Examples via Claude
```
- "Find upbeat electronic music under 30 seconds"
- "Search for energetic acoustic guitar loops with Creative Commons licensing"
- "Look for floating cities vibe background music"
- "Find ambient city sounds under 20 seconds"
```

#### Available Tools
- `search_sounds`: Search with natural language queries
  - Parameters: `query` (required), `max_results` (1-30, default 10)
  - Returns: File metadata, duration, format, tags, license info, preview URLs

#### Rate Limits
- **Free Tier:** 150 requests/hour (3,600/day)
- Sufficient for development and moderate production use

---

### 2. Freesound MCP Server (Node.js Alternative)
**Repository:** https://github.com/timjrobinson/FreesoundMCPServer  
**Stars:** 2  
**Language:** Node.js  
**Features:** More comprehensive API access (similar sounds, user sounds, packs)

#### Installation
```bash
git clone https://github.com/timjrobinson/FreesoundMCPServer.git
cd FreesoundMCPServer
npm install
npm run build
```

#### Claude Code Configuration
```bash
claude mcp add freesound -e FREESOUND_API_KEY=your-api-key-here -- node /path/to/FreesoundMCPServer/dist/index.js
```

#### Additional Tools (vs Python version)
- `get_sound`: Detailed information about specific sound
- `get_sound_analysis`: Audio analysis data (descriptors, normalized values)
- `get_similar_sounds`: Find similar sounds to a reference
- `get_user_sounds`: Get sounds from specific uploader
- `get_pack`: Information about sound packs
- `get_pack_sounds`: Get sounds from a specific pack

---

### 3. Remotion Superpowers Plugin (Music Generation)
**Repository:** https://github.com/DojoCodingLabs/remotion-superpowers  
**Stars:** 47  
**Type:** Claude Code plugin (not standalone MCP)  
**Features:** Full video production with audio generation

#### Audio Capabilities
- **Music Generation:** Suno API (via KIE - Kino Industry Engine)
- **Voiceovers:** ElevenLabs TTS
- **Sound Effects:** ElevenLabs SFX
- **Transcription:** Audio/video to text with timestamps

#### Commands (via plugin)
- `/add-music`: Generate and add background music by description
- `/add-voiceover`: Generate narration from script
- `/transcribe`: Transcribe audio/video to text

#### Note
This is a Claude Code plugin, not a standalone MCP server. Requires Remotion setup and KIE API access.

---

## DIRECT API INTEGRATION (Python Libraries)

### 1. Jamendo API (PRIMARY RECOMMENDATION)
**Best for:** Creative Commons music discovery by text description  
**Tracks:** 500,000+ with CC licensing built-in  
**Free Tier:** 35,000 API requests/month (non-commercial)

#### Installation
```bash
pip install requests python-dotenv
```

#### Setup
1. Register at https://developer.jamendo.com/
2. Create OAuth2 app credentials
3. Add to `.env`:
```env
JAMENDO_CLIENT_ID=your_client_id
JAMENDO_ACCESS_TOKEN=your_access_token
```

#### Python Example
```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("JAMENDO_CLIENT_ID")
access_token = os.getenv("JAMENDO_ACCESS_TOKEN")

params = {
    "client_id": client_id,
    "access_token": access_token,
    "searchquery": "upbeat electronic floating cities",
    "license": "cc_by",  # Options: cc_by, cc_by_sa, cc_by_nc, cc0
    "order": "popularity_week",
    "limit": 20,
    "format": "json"
}

response = requests.get("https://api.jamendo.com/v3.0/tracks/", params=params)
tracks = response.json()["results"]

for track in tracks:
    print(f"{track['name']} by {track['artist_name']}")
    print(f"  Download: {track['audio']}")
    print(f"  License: {track['license']}")
    print(f"  Duration: {track['duration']}s")
    print()
```

#### License Filtering
- `cc_by`: Creative Commons Attribution (commercial use OK with attribution)
- `cc_by_sa`: Share-Alike (must use same license for derivatives)
- `cc_by_nc`: Non-Commercial (free projects only)
- `cc0`: Public Domain (no attribution required)

#### Rate Limits
- 35,000 requests/month = ~1,200 requests/day
- Very generous for development and production

---

### 2. Freesound Python Library
**Best for:** Variety + sound effects mixed with music  
**Sounds:** 300,000+ with Creative Commons licensing  
**Free Tier:** 150 requests/hour

#### Installation
```bash
pip install git+https://github.com/MTG/freesound-python
```

#### Setup
1. Register at https://freesound.org/help/developers/
2. Get API key
3. Add to `.env`:
```env
FREESOUND_API_KEY=your_api_key
```

#### Python Example
```python
import freesound
import os
from dotenv import load_dotenv

load_dotenv()

client = freesound.FreesoundClient()
client.set_token(os.getenv("FREESOUND_API_KEY"))

results = client.text_search(
    query="upbeat electronic background music",
    fields="id,name,previews,license,duration,tags",
    filter='license:"Creative Commons Attribution" duration:[300 TO 600]',
    sort="rating-desc"
)

for sound in results:
    print(f"{sound.name}")
    print(f"  Preview: {sound.previews.get('preview-hq-mp3')}")
    print(f"  License: {sound.license}")
    print(f"  Duration: {sound.duration}s")
    print(f"  Tags: {', '.join(sound.tags[:5])}")
    print()
```

#### Advanced Filtering
```python
# Filter by duration (in seconds)
filter='duration:[10 TO 30]'

# Filter by license
filter='license:"Creative Commons Attribution"'

# Combine filters
filter='license:"Creative Commons Attribution" duration:[10 TO 30] tag:upbeat'

# Exclude dark/horror sounds
filter='license:"Creative Commons Attribution" -tag:dark -tag:horror -tag:drone'
```

#### Rate Limits
- 150 requests/hour = 3,600 requests/day
- Cache results to avoid re-querying

---

### 3. Pixabay Music API
**Tracks:** 30,000+ royalty-free music and sound effects  
**Free Tier:** 5,000 requests/day  
**License:** Pixabay License (free for commercial use)

#### Installation
```bash
pip install requests
```

#### Setup
1. Register at https://pixabay.com/api/docs/
2. Get API key
3. Add to `.env`:
```env
PIXABAY_API_KEY=your_api_key
```

#### Python Example
```python
import requests
import os

api_key = os.getenv("PIXABAY_API_KEY")

params = {
    "key": api_key,
    "q": "upbeat electronic",
    "type": "music",  # Options: music, sound_effect, all
    "per_page": 20
}

response = requests.get("https://pixabay.com/api/music/", params=params)
tracks = response.json()["hits"]

for track in tracks:
    print(f"{track['title']} by {track['artist']}")
    print(f"  URL: {track['url']}")
    print(f"  Duration: {track['duration']}s")
    print(f"  Tags: {track['tags']}")
    print()
```

---

## COMPARISON MATRIX

| Feature | Jamendo | Freesound | Pixabay | Remotion MCP |
|---------|---------|-----------|---------|--------------|
| **CC Music** | ✓✓ Best (500k+) | ✓✓ Good (300k+) | ✓ Limited (30k+) | ❌ Generated |
| **Python Library** | ❌ (use requests) | ✓ Official | ❌ (use requests) | N/A |
| **MCP Server** | ❌ No | ✓✓ Yes (2 options) | ❌ No | ✓ Plugin |
| **Text Search** | ✓ Full | ✓ Full | ✓ Full | ✓ Generation |
| **License Filter** | ✓ Built-in | ✓ Built-in | ✓ All same | N/A |
| **Download URLs** | ✓ Direct | ✓ Preview + Full | ✓ Direct | ✓ Generated |
| **Free Tier** | ✓ 35k/mo | ✓ 150/hr | ✓ 5k/day | Paid API |
| **Commercial Use** | ✓ CC-BY | ✓ CC-BY | ✓ Yes | ✓ Yes |
| **Rate Limits** | 1,200/day | 3,600/day | 5,000/day | API limits |
| **Setup Complexity** | OAuth2 | API key | API key | Multi-API |

---

## UNIFIED PYTHON IMPLEMENTATION

Create `src/videoreel/audio_finder.py`:

```python
import requests
import freesound
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

class AudioFinder:
    """Unified audio search across multiple Creative Commons sources"""
    
    def __init__(self):
        # Jamendo setup
        self.jamendo_id = os.getenv("JAMENDO_CLIENT_ID")
        self.jamendo_token = os.getenv("JAMENDO_ACCESS_TOKEN")
        
        # Freesound setup
        self.freesound = freesound.FreesoundClient()
        freesound_key = os.getenv("FREESOUND_API_KEY")
        if freesound_key:
            self.freesound.set_token(freesound_key)
        
        # Pixabay setup
        self.pixabay_key = os.getenv("PIXABAY_API_KEY")
    
    def find_music(
        self,
        mood: str,
        min_duration: int = 10,
        max_duration: int = 30,
        license_type: str = "cc_by",
        exclude_tags: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Find music by text description across all sources
        
        Args:
            mood: Text description ("upbeat electronic", "calm ambient")
            min_duration: Minimum duration in seconds
            max_duration: Maximum duration in seconds
            license_type: License filter (cc_by, cc_by_sa, cc_by_nc, cc0)
            exclude_tags: Tags to exclude (e.g., ["dark", "horror", "drone"])
        
        Returns:
            List of tracks with metadata and download URLs
        """
        results = []
        exclude_tags = exclude_tags or ["dark", "horror", "drone", "atonal"]
        
        # Primary: Jamendo (best CC music selection)
        jamendo_tracks = self._search_jamendo(mood, license_type, min_duration, max_duration)
        results.extend(jamendo_tracks)
        
        # Secondary: Freesound (for variety)
        if len(results) < 10:
            freesound_tracks = self._search_freesound(mood, min_duration, max_duration, exclude_tags)
            results.extend(freesound_tracks)
        
        # Tertiary: Pixabay (simple license, good for commercial)
        if len(results) < 10 and self.pixabay_key:
            pixabay_tracks = self._search_pixabay(mood)
            results.extend(pixabay_tracks)
        
        # Filter by exclude_tags across all sources
        results = [t for t in results if not any(
            tag.lower() in [et.lower() for et in exclude_tags]
            for tag in t.get("tags", [])
        )]
        
        return results
    
    def _search_jamendo(self, mood: str, license_type: str, min_dur: int, max_dur: int) -> List[Dict]:
        """Search Jamendo by mood"""
        if not self.jamendo_id or not self.jamendo_token:
            return []
        
        params = {
            "client_id": self.jamendo_id,
            "access_token": self.jamendo_token,
            "searchquery": mood,
            "license": license_type,
            "order": "popularity_week",
            "limit": 20,
            "format": "json",
            "audioformat": "mp32",  # MP3 320kbps
        }
        
        try:
            resp = requests.get("https://api.jamendo.com/v3.0/tracks/", params=params, timeout=10)
            resp.raise_for_status()
            
            tracks = []
            for t in resp.json().get("results", []):
                duration = t.get("duration", 0)
                if min_dur <= duration <= max_dur:
                    tracks.append({
                        "source": "jamendo",
                        "id": t["id"],
                        "name": t["name"],
                        "artist": t["artist_name"],
                        "url": t["audio"],
                        "license": t["license"],
                        "tags": [tag["name"] for tag in t.get("tags", [])],
                        "duration": duration
                    })
            
            return tracks
        except Exception as e:
            print(f"Jamendo error: {e}")
            return []
    
    def _search_freesound(self, mood: str, min_dur: int, max_dur: int, exclude_tags: List[str]) -> List[Dict]:
        """Search Freesound by mood"""
        if not self.freesound:
            return []
        
        try:
            # Build filter with duration and exclusions
            exclude_filter = " ".join([f'-tag:{tag}' for tag in exclude_tags])
            filter_str = f'license:"Creative Commons Attribution" duration:[{min_dur} TO {max_dur}] {exclude_filter}'
            
            results = self.freesound.text_search(
                query=mood,
                fields="id,name,previews,license,duration,tags",
                filter=filter_str,
                sort="rating_desc",
                page_size=20
            )
            
            tracks = []
            for s in results:
                if s.previews and s.previews.get("preview-hq-mp3"):
                    tracks.append({
                        "source": "freesound",
                        "id": s.id,
                        "name": s.name,
                        "url": s.previews.get("preview-hq-mp3"),
                        "license": s.license,
                        "tags": s.tags if hasattr(s, 'tags') else [],
                        "duration": s.duration if hasattr(s, 'duration') else 0
                    })
            
            return tracks[:10]
        except Exception as e:
            print(f"Freesound error: {e}")
            return []
    
    def _search_pixabay(self, mood: str) -> List[Dict]:
        """Search Pixabay by mood"""
        if not self.pixabay_key:
            return []
        
        params = {
            "key": self.pixabay_key,
            "q": mood,
            "type": "music",
            "per_page": 20
        }
        
        try:
            resp = requests.get("https://pixabay.com/api/music/", params=params, timeout=10)
            resp.raise_for_status()
            
            return [{
                "source": "pixabay",
                "id": t["id"],
                "name": t["title"],
                "artist": t["artist"],
                "url": t["url"],
                "license": "Pixabay License (free commercial)",
                "tags": t["tags"].split(", "),
                "duration": t["duration"]
            } for t in resp.json().get("hits", [])]
        except Exception as e:
            print(f"Pixabay error: {e}")
            return []


# Example usage
if __name__ == "__main__":
    finder = AudioFinder()
    
    # Find upbeat electronic music for 20-second clips
    tracks = finder.find_music(
        mood="energetic acoustic floating cities aesthetic",
        min_duration=15,
        max_duration=25,
        license_type="cc_by",
        exclude_tags=["dark", "horror", "drone"]
    )
    
    print(f"Found {len(tracks)} tracks:\n")
    
    for track in tracks[:5]:
        print(f"🎵 {track['name']} ({track['source']})")
        print(f"   Artist: {track['artist']}")
        print(f"   Duration: {track['duration']}s")
        print(f"   License: {track['license']}")
        print(f"   URL: {track['url']}")
        print(f"   Tags: {', '.join(track['tags'][:5])}")
        print()
```

---

## RECOMMENDED SETUP

### 1. Install Dependencies
```bash
pip install requests git+https://github.com/MTG/freesound-python python-dotenv
```

### 2. Register for API Keys

#### Jamendo (Primary - Best CC Music)
1. Go to https://developer.jamendo.com/
2. Create account and register new app
3. Get Client ID and Access Token

#### Freesound (Secondary - Variety)
1. Go to https://freesound.org/help/developers/
2. Create account and apply for API key
3. Wait for approval (usually within 24 hours)

#### Pixabay (Optional - Simple License)
1. Go to https://pixabay.com/api/docs/
2. Create account and get API key (instant)

### 3. Configure Environment
Create `.env` in project root:
```env
# Jamendo (OAuth2)
JAMENDO_CLIENT_ID=your_client_id_here
JAMENDO_ACCESS_TOKEN=your_access_token_here

# Freesound (API Key)
FREESOUND_API_KEY=your_api_key_here

# Pixabay (Optional)
PIXABAY_API_KEY=your_api_key_here
```

### 4. Add to .gitignore
```bash
echo ".env" >> .gitignore
```

---

## FILTERING DARK/HORROR SOUNDS

### Recommended Exclusion Tags
```python
exclude_tags = [
    "dark",
    "horror",
    "drone",
    "atonal",
    "creepy",
    "scary",
    "eerie",
    "ominous",
    "suspense",
    "tension"
]
```

### Positive Search Terms for Viral Music
```python
viral_moods = [
    "upbeat electronic floating cities",
    "energetic acoustic indie",
    "happy uplifting corporate",
    "positive motivational",
    "bright cheerful acoustic",
    "modern electronic dance",
    "inspiring cinematic orchestral",
    "chill lofi hip hop",
    "tropical house summer",
    "indie folk acoustic guitar"
]
```

---

## IMPORTANT GOTCHAS

### License Attribution Requirements
- **CC-BY:** Requires artist credit in video description/metadata
- **CC-BY-SA:** Must use same license for derivative work
- **CC-BY-NC:** Non-commercial use only (no monetization)
- **CC0/Pixabay:** No attribution required (best for simplicity)

### Preview vs. Full Quality
- **Freesound:** Previews are preview quality (MP3 128kbps HQ preview available)
- **Jamendo:** Provides full-quality downloads (MP3 320kbps)
- **Pixabay:** Provides full-quality downloads (MP3 320kbps)

### Rate Limit Strategy
```python
# Cache results to avoid re-querying
import json
from pathlib import Path

cache_file = Path(".audio_cache.json")

def get_cached_or_search(mood, finder):
    if cache_file.exists():
        cache = json.loads(cache_file.read_text())
        if mood in cache:
            return cache[mood]
    
    results = finder.find_music(mood)
    
    # Update cache
    cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    cache[mood] = results
    cache_file.write_text(json.dumps(cache, indent=2))
    
    return results
```

---

## NEXT STEPS FOR VIDEOREEL GENERATOR

1. **Add audio_finder.py** to `src/videoreel/` directory
2. **Register for API keys** (Jamendo primary, Freesound secondary)
3. **Integrate with scene classification:**
   - Analyze scene motion/complexity → map to mood
   - High motion = "energetic", low motion = "calm"
4. **Add audio overlay to pipeline:**
   ```python
   # In segment_extractor.py
   from .audio_finder import AudioFinder
   
   finder = AudioFinder()
   tracks = finder.find_music("upbeat electronic", min_duration=15, max_duration=25)
   selected_track = tracks[0]  # Or rank by tags/popularity
   
   # Overlay audio on video segment
   # (Use ffmpeg or moviepy for audio overlay)
   ```
5. **Test with sample video** (5-10 minutes)
6. **Verify license compliance** (add attribution to metadata)

---

## RESOURCES

### Documentation
- **Jamendo API:** https://developer.jamendo.com/v3.0
- **Freesound API:** https://freesound.org/docs/api/
- **Pixabay API:** https://pixabay.com/api/docs/

### Python Libraries
- **Freesound Python:** https://github.com/MTG/freesound-python
- **Requests:** https://requests.readthedocs.io/

### MCP Servers
- **Freesound MCP (Python):** https://github.com/johnkimdw/freesound-mcp-server
- **Freesound MCP (Node.js):** https://github.com/timjrobinson/FreesoundMCPServer
- **Remotion Superpowers:** https://github.com/DojoCodingLabs/remotion-superpowers

---

## SUMMARY RECOMMENDATION

**For your VideoReel Generator project:**

1. **Install Freesound MCP** (for Claude Desktop integration during development)
2. **Use Jamendo API** (primary, for Python production code - best CC music selection)
3. **Use Freesound API** (secondary, for variety and sound effects)
4. **Implement unified AudioFinder class** (above) for multi-source search
5. **Cache results** to stay within rate limits
6. **Filter dark/horror sounds** by excluded tags
7. **Map scene classification to mood** (high motion → energetic, etc.)

This gives you both interactive MCP access during development and robust Python API integration for production.

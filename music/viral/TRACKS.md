# Viral-Ready Music Tracks

5 upbeat, energetic Creative Commons tracks perfect for 5-20 second video reels.

## How to Download

Freesound CDN blocks automated downloads. Manual download required:

1. Click track links below
2. Click blue "Download" button (requires free Freesound account)
3. Save to `music/viral/` directory with the filename shown

---

## Track 1: Uplifting Background Music
**Filename:** `01_uplifting_presentations_viramiller.mp3`  
**Artist:** ViraMiller  
**Duration:** 21.4 seconds  
**License:** CC-BY 4.0  
**URL:** https://freesound.org/people/ViraMiller/sounds/746677/  
**Hook Timing:** 0:00 - Energy starts immediately  
**Why Viral:** Short duration perfect for reels, professional cheerful energy, 3,200+ downloads  
**Credit:** "Music by ViraMiller / freesound.org"

---

## Track 2: 90's Smooth Funk
**Filename:** `02_90s_smooth_funk_yellowtree.mp3`  
**Artist:** YellowTree  
**Duration:** 31.8 seconds  
**License:** CC-BY 4.0  
**URL:** https://freesound.org/people/YellowTree/sounds/621091/  
**Hook Timing:** 0:00-0:05 - Funk groove starts immediately  
**Why Viral:** Authentic 90s pop/funk at 84 BPM, groovy bassline, retro aesthetic, 1,500+ downloads  
**Credit:** "Music by YellowTree / freesound.org"

---

## Track 3: Cheerful and Upbeat Tune
**Filename:** `03_cheerful_happy_universfield.mp3`  
**Artist:** Gustavo_Alivera (UNIVERSFIELD)  
**Duration:** 93.4 seconds  
**License:** CC-BY 4.0  
**URL:** https://freesound.org/people/Gustavo_Alivera/sounds/769380/  
**Hook Timing:** 0:00-0:08 - Lively melody hooks early  
**Why Viral:** "Wii Sports Resort" vibes, extremely vibrant and dynamic, 320kbps quality, 1,200+ downloads  
**Credit:** "Music by Gustavo_Alivera / freesound.org"

---

## Track 4: Happy Background Music Orchestra
**Filename:** `04_happy_orchestra_loop_migfus20.mp3`  
**Artist:** Migfus20  
**Duration:** 52.6 seconds  
**License:** CC-BY 4.0  
**URL:** https://freesound.org/people/Migfus20/sounds/561383/  
**Hook Timing:** 0:00 - Orchestra establishes happy mood immediately  
**Why Viral:** Orchestral loop, 5,200+ downloads (most popular), loops seamlessly  
**Credit:** "Music by Migfus20 / freesound.org"

---

## Track 5: Vibrant and Uplifting Energy
**Filename:** `05_vibrant_uplifting_matio888.mp3`  
**Artist:** Matio888  
**Duration:** 83.1 seconds  
**License:** CC-BY 4.0  
**URL:** https://freesound.org/people/Matio888/sounds/789329/  
**Hook Timing:** 0:00-0:06 - Vibrant energy kicks in immediately  
**Why Viral:** Dynamic, fast-paced, feel-good, 320kbps quality, motivating and cheerful  
**Credit:** "Music by Matio888 / freesound.org"

---

## Bonus Track: Funky Jazz Loop
**Filename:** `06_july_funk_loop_rhodesmas.mp3`  
**Artist:** rhodesmas  
**Duration:** 17.5 seconds  
**License:** CC-BY 4.0  
**URL:** https://freesound.org/people/rhodesmas/sounds/323545/  
**Hook Timing:** 0:00 - Funky groove starts instantly  
**Why Viral:** Sophisticated funk with Wurlitzer keys, 3,600+ downloads, loops perfectly  
**Credit:** "Music by rhodesmas / freesound.org"

---

## License Requirements

All tracks are **CC-BY 4.0** (Creative Commons Attribution):
- ✓ Commercial use allowed
- ✓ Modifications allowed
- ✓ Must provide attribution

**Attribution Format:**
```
Music by [Artist Name] / freesound.org
```

Include in video description, credits, or on-screen text.

---

## Quick Download Script

```bash
# Visit each URL above
# Click "Download" button (login required)
# Save files to: music/viral/

# Or use this command if you have the downloads:
cd ~/Downloads
mv "Uplifting Background Music*" music/viral/01_uplifting_presentations_viramiller.mp3
mv "90s Smooth Funk*" music/viral/02_90s_smooth_funk_yellowtree.mp3
# ... etc
```

---

## Testing Tracks

After downloading, test with:

```bash
# Extract one reel with random music
python3 extract_reels_with_music.py video.mp4 -n 1 --target-duration 20

# Preview all tracks
for f in music/viral/*.mp3; do 
    echo "Playing: $f"
    ffplay -nodisp -autoexit "$f"
done
```

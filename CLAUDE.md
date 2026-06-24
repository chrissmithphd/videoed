# VideoReel Generator - Project Context

## Project Overview

**Name:** VideoReel Generator  
**Goal:** Intelligent extraction of interesting 20-second segments from long-form videos (30min-2hr+)  
**Primary Language:** Python 3.10+  
**Status:** Research Complete → Ready for Prototyping

## What This Does

Takes long videos and automatically:
1. Detects natural scene boundaries
2. Analyzes each scene for "interestingness" (motion, visual complexity, objects)
3. Ranks and selects top segments
4. Extracts 20-second clips with quality preservation

Future: Add audio and text overlays to extracted reels.

## Current Architecture

### Recommended Tech Stack
- **PyAV (v17.1.0)** - Video I/O with FFmpeg bindings (quality preservation)
- **PySceneDetect (v0.7)** - Scene boundary detection
- **OpenCV (v4.13+)** - Motion analysis via optical flow
- **Optional: Ultralytics YOLO (v8.4+)** - ML-based object detection (GPU)

### Pipeline Flow
```
Video Input → Scene Detection → Interest Scoring → Ranking → Segment Extraction → Reels
```

### Interest Scoring Formula
```python
score = (motion * 0.4) + (visual_complexity * 0.3) + (objects * 0.2) + (diversity * 0.1)
```

## Implementation Notes

### Quality Preservation Strategy
- **Preferred:** Codec copy (`ffmpeg -c copy`) for lossless extraction at keyframes
- **Fallback:** High-quality re-encode (`-crf 18`) when mid-scene cutting required

### Performance Characteristics
- Traditional CV: ~1x realtime on 8-core CPU (60min video = 45-60min processing)
- ML-Enhanced: ~0.5-1x realtime with GPU (60min video = 30-45min)
- Bottleneck: Frame-by-frame interest scoring
- Optimization: Frame sampling (process every Nth frame)

### Why These Libraries

**PyAV over MoviePy:**
- MoviePy too slow for long videos (high memory, poor performance)
- PyAV direct FFmpeg access = better quality control

**PySceneDetect:**
- Purpose-built, actively maintained (May 2026)
- Built-in progress tracking for long videos
- Multiple detection algorithms (ContentDetector, AdaptiveDetector, ThresholdDetector)

**OpenCV for Motion:**
- Mature, fast, well-documented
- Dense optical flow (Farneback algorithm) for comprehensive motion analysis
- GPU acceleration available via CUDA

**YOLO (Optional):**
- State-of-art object detection (1.7-11.8ms/frame on GPU)
- Real-time tracking built-in
- Warning: AGPL-3.0 license (enterprise requires paid license)

## Project Structure

```
videoed/
├── .claude/
│   └── plans/VideoReel-Generator/
│       └── current_plan.md          # Task tracking
├── CLAUDE.md                         # This file
├── README.md                         # Project documentation
├── RESEARCH.md                       # Detailed research findings
└── (future) src/videoreel/          # Implementation
    ├── __init__.py
    ├── scene_detector.py
    ├── motion_analyzer.py
    ├── interest_scorer.py
    ├── segment_extractor.py
    └── cli.py
```

## Key Decisions

1. **Python preference confirmed** - Rich ecosystem, all recommended libraries Python-native
2. **CPU-first approach** - Traditional CV works well without GPU, ML optional enhancement
3. **Scene-based processing** - Reduces search space, more efficient than frame-by-frame for entire video
4. **Composite scoring** - Multiple metrics better than single-dimensional (motion-only)
5. **Quality over speed** - Codec copy when possible, high-quality re-encode otherwise

## Gotchas & Important Notes

### Library Selection Traps
- ❌ **Avoid MoviePy** for long videos - memory issues, slow performance
- ⚠️ **ffmpeg-python** not maintained since 2019 (but still functional)
- ⚠️ **Decord** is alpha status with limited maintenance

### Video Processing Pitfalls
- Codec copy only works at keyframe boundaries
- Long videos require streaming approaches (don't load entire video into memory)
- Scene detection thresholds very content-dependent (need experimentation)
- Optical flow expensive - frame sampling critical for performance

### ML Considerations
- YOLO requires GPU for real-time on long videos
- Model download on first run (~6-50MB depending on variant)
- AGPL-3.0 license requires attention for commercial use
- CPU-only YOLO is 10-20x slower than GPU

## Installation Commands

### Minimal (CPU Only)
```bash
pip install opencv-python scenedetect av numpy
sudo apt-get install ffmpeg  # or brew install ffmpeg
```

### Full (ML-Enhanced)
```bash
pip install opencv-python scenedetect av numpy ultralytics torch
pip install torch --index-url https://download.pytorch.org/whl/cu121  # CUDA 12.1
```

## Next Session Guidance

### If Starting Prototyping:
1. Create `src/videoreel/` directory structure
2. Start with scene_detector.py wrapper around PySceneDetect
3. Implement motion_analyzer.py with OpenCV optical flow
4. Test with short sample video (~5min) before scaling to long videos
5. Add progress bars (tqdm) early - critical for long video UX

### If Continuing Research:
- Audio overlay: Research librosa, pydub, or MoviePy audio handling
- Text overlay: Research Pillow + OpenCV or MoviePy TextClip
- Speech-to-text: Research OpenAI Whisper for auto-captioning

### Testing Strategy:
- Unit tests: Individual scoring functions
- Integration tests: End-to-end pipeline with known-good video
- Performance tests: Benchmark with 30min, 60min, 120min videos
- Sample videos: Download Creative Commons test content

## References

### Primary Documentation
- PyAV: https://pyav.org/docs/stable/
- PySceneDetect: https://scenedetect.com
- OpenCV: https://docs.opencv.org/4.x/
- YOLO: https://docs.ultralytics.com/

### Key GitHub Repos
- PyAV: https://github.com/PyAV-Org/PyAV (3.2k stars, active)
- PySceneDetect: https://github.com/Breakthrough/PySceneDetect (4.9k stars, active)
- Ultralytics: https://github.com/ultralytics/ultralytics (very active, updated June 2026)

---

**Research completed:** 2026-06-24  
**Research agent ID:** a0d77fa9b06644079 (35k tokens, comprehensive analysis)  
**Current plan:** `.claude/plans/VideoReel-Generator/current_plan.md`

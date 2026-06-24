# VideoReel Generator - Research Documentation

**Date Started:** 2026-06-24  
**Focus:** Video parsing and intelligent segment extraction

---

## Research Progress

### 1. Video Processing Libraries (Python)

#### ✅ Completed - See detailed findings below

**Recommended Stack:**
- **PyAV v17.1.0** - Direct FFmpeg bindings, excellent quality preservation (Last updated: June 2026)
- **PySceneDetect v0.7** - Scene detection with multiple algorithms (Last updated: May 2026)
- **OpenCV v4.13.0.92** - Motion detection and analysis (Last updated: Feb 2026)
- **Ultralytics YOLO v8.4.76** (Optional) - ML-based object detection for interest scoring (Last updated: June 2026)

**Key Findings:**
1. **PyAV** provides best quality preservation with codec copying (no re-encoding)
2. **PySceneDetect** is purpose-built, actively maintained, with progress tracking for long videos
3. **OpenCV** offers fast optical flow and background subtraction for motion analysis
4. **YOLO** adds sophisticated object-based interest detection (requires GPU)

**Avoid:**
- **MoviePy** - Too slow for 30min-2hr videos, high memory usage
- **ffmpeg-python** - No updates since 2019 (though still functional)
- **Decord** - Alpha status, limited maintenance

---

### 2. Scene Detection Approaches

#### ✅ Completed

**PySceneDetect Detection Methods:**

1. **ContentDetector** - Fast scene cuts via HSV color space analysis
   - Best for: Hard cuts, quick transitions
   - Speed: Fast
   
2. **AdaptiveDetector** - Two-pass rolling average of HSL changes
   - Best for: Camera movement, gradual transitions
   - Speed: Medium
   
3. **ThresholdDetector** - Fade in/out detection
   - Best for: Identifying fades and dissolves
   - Speed: Fast

**Recommendation:** Start with `ContentDetector` for most use cases, combine with `AdaptiveDetector` if video has significant camera motion.

---

### 3. Motion Detection Techniques

#### ✅ Completed

**Three Primary Approaches:**

**A. Optical Flow (OpenCV)**
- **Sparse (Lucas-Kanade):** Track selected points, fast, real-time capable
  - Use case: Point tracking, feature-based motion
  - Function: `cv2.calcOpticalFlowPyrLK()`
  
- **Dense (Farneback):** Full pixel motion field
  - Use case: Complete motion analysis, detailed visualization
  - Function: `cv2.calcOpticalFlowFarneback()`

**B. Background Subtraction**
- **MOG2:** Gaussian mixture modeling, adaptive, shadow detection
  - Function: `cv2.createBackgroundSubtractorMOG2()`
  
- **KNN:** K-nearest neighbors approach
  - Function: `cv2.createBackgroundSubtractorKNN()`
  
- Best for: Static camera, surveillance-style motion detection

**C. Frame Differencing**
- Simple absolute difference between frames
- Fastest approach but least robust
- Good for initial motion screening

**Recommendation:** Use **Dense Optical Flow** for comprehensive motion analysis in dynamic camera scenarios.

---

### 4. Activity/Interest Scoring Methods

#### ✅ Completed

**Multi-Metric Composite Scoring Approach:**

**Traditional CV Metrics:**
1. **Motion Magnitude** (Optical Flow) - Detects movement intensity
2. **Visual Complexity** (Canny Edge Detection) - Measures scene detail
3. **Color Variance** - Identifies vibrant/varied scenes
4. **Face/Person Detection** - Human presence indicator

**ML-Based Metrics (YOLO):**
1. **Object Count** - Number of detected objects
2. **Object Diversity** - Unique object classes present
3. **Pose Estimation** - Human activity/action recognition

**Composite Scoring Function:**
```python
interest_score = (
    motion_score * 0.4 +
    visual_complexity * 0.3 +
    object_count * 0.2 +
    object_diversity * 0.1
)
```

**Recommendation:** Start with motion + complexity (traditional CV), add YOLO if GPU available and higher accuracy needed.

---

### 5. Segment Extraction Strategy

#### ✅ Completed

**Two-Phase Approach:**

**Phase 1: Scene Detection**
- Use PySceneDetect to identify natural scene boundaries
- Reduces search space from entire video to discrete scenes

**Phase 2: Interest Scoring Within Scenes**
- Sample frames within each scene (e.g., every 10 frames)
- Calculate composite interest score per scene
- Rank scenes by average interest score

**20-Second Segment Extraction Options:**

1. **Exact 20 seconds:** Extract precisely 20s from scene start
2. **Centered 20 seconds:** Center extraction on highest-scoring moment
3. **Best 20 seconds:** Sliding window to find optimal 20s within scene

**Quality Preservation:**
```bash
# Codec copy (fastest, lossless)
ffmpeg -i input.mp4 -ss 60 -t 20 -c copy output.mp4

# High-quality re-encode (if cutting not on keyframe)
ffmpeg -i input.mp4 -ss 60 -t 20 -c:v libx264 -crf 18 -c:a copy output.mp4
```

**Recommendation:** Use codec copy where possible, re-encode only when necessary (mid-scene cuts).

---

### 6. Implementation Architecture

#### ✅ Completed

**Proposed Pipeline Architecture:**

```
Long Video Input (30min-2hr)
         ↓
[1] Scene Detection (PySceneDetect)
    → Identifies scene boundaries
         ↓
[2] Scene Analysis (OpenCV + Optional YOLO)
    → Calculates interest scores per scene
    → Samples frames for efficiency
         ↓
[3] Scene Ranking
    → Sorts scenes by composite interest score
    → Selects top N scenes
         ↓
[4] Segment Extraction (PyAV/FFmpeg)
    → Extracts 20-second segments
    → Preserves quality (codec copy)
         ↓
[5] Post-Processing (Future Phase)
    → Audio overlay
    → Text/caption overlay
    → Transitions/effects
         ↓
Output: N interesting 20-second reels
```

**Performance Characteristics:**
- **Traditional CV Pipeline:** ~1-2x realtime on CPU (30min video → 30-60min processing)
- **ML-Enhanced Pipeline:** ~0.5-1x realtime on GPU (30min video → 30-60min processing)
- **Bottleneck:** Interest scoring (frame-by-frame analysis)

**Optimization Strategies:**
1. Frame sampling (process every Nth frame)
2. GPU acceleration (CUDA-enabled OpenCV + YOLO)
3. Multi-threading (process scenes in parallel)
4. Early termination (stop after finding N good segments)

---

## Detailed Library Analysis

### Core Video Processing

#### PyAV (Recommended)
- **Version:** 17.1.0 (June 2026)
- **Maintenance:** Active, well-maintained
- **Pros:** Direct FFmpeg bindings, precise control, excellent quality
- **Cons:** Steeper learning curve
- **Installation:** `pip install av`
- **Docs:** https://pyav.org/docs/stable/
- **GitHub:** https://github.com/PyAV-Org/PyAV (3.2k stars)

#### VidGear (Alternative)
- **Version:** 0.3.5 (May 2026)
- **Maintenance:** Active
- **Pros:** Multi-threaded, excellent for streaming, keyframe-selective processing
- **Cons:** More complex API
- **Installation:** `pip install vidgear[core]`
- **Docs:** https://abhitronix.github.io/vidgear/
- **GitHub:** https://github.com/abhiTronix/vidgear (3.7k stars)

#### ffmpeg-python (Functional but dated)
- **Version:** 0.2.0 (July 2019)
- **Maintenance:** Limited (last PyPI 2019, some GitHub activity 2024)
- **Pros:** Simple, declarative, good for basic pipelines
- **Cons:** Stagnant development, 525 open issues
- **Recommendation:** Use if simplicity > latest features

#### MoviePy (Not Recommended)
- **Version:** 2.2.1 (May 2025)
- **Maintenance:** Active but seeking maintainers
- **Pros:** High-level, easy API
- **Cons:** Too slow for long videos, high memory usage
- **Recommendation:** ❌ Avoid for 30min-2hr videos

#### OpenCV
- **Version:** 4.13.0.92 (Feb 2026)
- **Maintenance:** Very active
- **Pros:** Fast, comprehensive, hardware acceleration
- **Usage:** Motion analysis, frame extraction
- **Installation:** `pip install opencv-python`
- **Docs:** https://docs.opencv.org/4.x/

### Scene Detection

#### PySceneDetect (Primary)
- **Version:** 0.7 (May 2026)
- **Maintenance:** Active, mature project
- **Pros:** Purpose-built, CLI + API, progress tracking
- **Installation:** `pip install scenedetect[opencv]`
- **Docs:** https://scenedetect.com
- **GitHub:** https://github.com/Breakthrough/PySceneDetect (4.9k stars)

### Object Detection

#### Ultralytics YOLO (Optional, ML-Enhanced)
- **Version:** 8.4.76 (June 2026)
- **Maintenance:** Very active (updated today)
- **Pros:** State-of-art, fast (1.7-11.8ms/frame on GPU), tracking built-in
- **Cons:** Requires GPU for speed, AGPL-3.0 license
- **Installation:** `pip install ultralytics`
- **Docs:** https://docs.ultralytics.com/
- **GitHub:** https://github.com/ultralytics/ultralytics

---

## Code Examples

### Example 1: Basic Scene Detection
```python
from scenedetect import detect, ContentDetector, split_video_ffmpeg

# Detect scenes
scenes = detect('video.mp4', ContentDetector(threshold=27.0), show_progress=True)

# Print scene list
for i, (start, end) in enumerate(scenes):
    print(f"Scene {i}: {start.get_seconds():.2f}s - {end.get_seconds():.2f}s")

# Auto-split video
split_video_ffmpeg('video.mp4', scenes, output_dir='scenes/')
```

### Example 2: Motion Detection with Optical Flow
```python
import cv2
import numpy as np

cap = cv2.VideoCapture('video.mp4')
ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate dense optical flow
    flow = cv2.calcOpticalFlowFarneback(
        prev_gray, gray, None,
        pyr_scale=0.5, levels=3, winsize=15,
        iterations=3, poly_n=5, poly_sigma=1.2, flags=0
    )
    
    # Calculate motion magnitude
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    avg_motion = np.mean(magnitude)
    
    print(f"Motion score: {avg_motion:.2f}")
    
    prev_gray = gray

cap.release()
```

### Example 3: YOLO Object Detection
```python
from ultralytics import YOLO

model = YOLO("yolo26n.pt")  # Nano model for speed

results = model("video.mp4", stream=True, verbose=False)

for frame_idx, result in enumerate(results):
    boxes = result.boxes
    num_objects = len(boxes)
    unique_classes = len(set(boxes.cls.tolist()))
    
    print(f"Frame {frame_idx}: {num_objects} objects, {unique_classes} classes")
```

### Example 4: Complete Traditional CV Pipeline
```python
import cv2
import numpy as np
from scenedetect import detect, ContentDetector
import subprocess

# Step 1: Detect scenes
print("Detecting scenes...")
scenes = detect('long_video.mp4', ContentDetector(threshold=27.0), show_progress=True)

# Step 2: Score scenes by motion
print("Analyzing motion...")
cap = cv2.VideoCapture('long_video.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)

scene_scores = []

for scene_idx, (start_time, end_time) in enumerate(scenes):
    start_frame = int(start_time.get_seconds() * fps)
    end_frame = int(end_time.get_seconds() * fps)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    motion_scores = []
    ret, prev_frame = cap.read()
    if not ret:
        continue
    
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    
    # Sample every 10 frames
    for frame_idx in range(start_frame + 1, end_frame, 10):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate optical flow
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, gray, None,
            0.5, 3, 15, 3, 5, 1.2, 0
        )
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        motion_scores.append(np.mean(magnitude))
        
        prev_gray = gray
    
    avg_motion = np.mean(motion_scores) if motion_scores else 0
    scene_scores.append({
        'scene_idx': scene_idx,
        'start': start_time.get_seconds(),
        'end': end_time.get_seconds(),
        'duration': end_time.get_seconds() - start_time.get_seconds(),
        'motion_score': avg_motion
    })
    
    print(f"Scene {scene_idx}: {avg_motion:.2f} motion")

cap.release()

# Step 3: Select top scenes
top_scenes = sorted(scene_scores, key=lambda x: x['motion_score'], reverse=True)[:10]

# Step 4: Extract 20-second segments
print("Extracting segments...")
for idx, scene in enumerate(top_scenes):
    clip_start = scene['start']
    duration = min(20, scene['duration'])
    
    output_file = f'reel_{idx:03d}_score_{scene["motion_score"]:.1f}.mp4'
    
    subprocess.run([
        'ffmpeg', '-i', 'long_video.mp4',
        '-ss', str(clip_start),
        '-t', str(duration),
        '-c', 'copy',  # Codec copy for quality
        '-y',  # Overwrite
        output_file
    ], capture_output=True)
    
    print(f"✓ Extracted: {output_file}")

print(f"\nComplete! Extracted {len(top_scenes)} interesting segments.")
```

---

## Installation Guide

### Minimal Setup (Traditional CV - No GPU Required)
```bash
# Core dependencies
pip install opencv-python scenedetect av numpy

# FFmpeg (required by PySceneDetect and PyAV)
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

### Full Setup (ML-Enhanced - GPU Recommended)
```bash
# All dependencies
pip install opencv-python scenedetect av numpy ultralytics torch

# For CUDA support (NVIDIA GPU):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Verify CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### Optional: High-Performance Setup
```bash
# VidGear for multi-threaded processing
pip install vidgear[core]

# GPU-accelerated OpenCV (if available)
pip uninstall opencv-python
pip install opencv-contrib-python

# Additional tools
pip install tqdm  # Progress bars
pip install librosa  # Audio analysis (future)
```

---

## Performance Benchmarks (Estimated)

**Test Video:** 60 minutes, 1080p, 30fps

| Pipeline | Hardware | Processing Time | Quality | Cost |
|----------|----------|----------------|---------|------|
| Traditional CV (OpenCV only) | CPU (8-core) | 60-90 min | Good | Free |
| Traditional CV + Scene Detection | CPU (8-core) | 45-60 min | Good | Free |
| ML-Enhanced (YOLO) | GPU (RTX 3060) | 30-45 min | Excellent | GPU req'd |
| ML-Enhanced (YOLO) | CPU only | 3-5 hours | Excellent | Free but slow |

**Optimization Tips:**
1. **Frame sampling:** Process every 5th or 10th frame (5-10x speedup)
2. **Scene pre-filtering:** Skip short scenes (<5s) or long scenes (>2min)
3. **Early termination:** Stop after finding desired number of segments
4. **Parallel processing:** Use multiprocessing for scene analysis
5. **GPU acceleration:** Use CUDA-enabled OpenCV + YOLO

---

## Next Steps

### Immediate (Research Complete)
- ✅ Video processing libraries researched
- ✅ Scene detection approaches documented
- ✅ Motion detection techniques identified
- ✅ Interest scoring methods defined
- ✅ Architecture designed

### Phase 2: Prototyping (Next)
- [ ] Set up development environment
- [ ] Install core dependencies (PyAV, PySceneDetect, OpenCV)
- [ ] Implement basic scene detection test
- [ ] Implement motion scoring test
- [ ] Create end-to-end prototype with sample video
- [ ] Benchmark performance on test videos

### Phase 3: Enhancement (Future)
- [ ] Audio overlay implementation
- [ ] Text/caption overlay implementation
- [ ] Transition effects
- [ ] Batch processing CLI tool
- [ ] Configuration file support (tunable thresholds)
- [ ] Web interface (optional)

---

## Open Questions

1. **Target video format:** Will input always be MP4, or need support for MOV, AVI, etc?
2. **Output requirements:** Specific resolution/bitrate for reels (Instagram, TikTok, YouTube Shorts)?
3. **Audio handling:** Keep original audio, add new audio, or both?
4. **Text overlay specs:** Manual captions or auto-generated (speech-to-text)?
5. **Batch vs. single:** Process one video at a time or batch multiple?
6. **GPU availability:** Development machine has NVIDIA GPU?

---

## References

### Primary Documentation
- PyAV: https://pyav.org/docs/stable/
- PySceneDetect: https://scenedetect.com
- OpenCV: https://docs.opencv.org/4.x/
- Ultralytics YOLO: https://docs.ultralytics.com/

### GitHub Repositories
- PyAV: https://github.com/PyAV-Org/PyAV
- PySceneDetect: https://github.com/Breakthrough/PySceneDetect
- OpenCV: https://github.com/opencv/opencv
- Ultralytics: https://github.com/ultralytics/ultralytics
- VidGear: https://github.com/abhiTronix/vidgear

### PyPI Packages
- av: https://pypi.org/project/av/
- scenedetect: https://pypi.org/project/scenedetect/
- opencv-python: https://pypi.org/project/opencv-python/
- ultralytics: https://pypi.org/project/ultralytics/
- vidgear: https://pypi.org/project/vidgear/

---

*Research completed: 2026-06-24*


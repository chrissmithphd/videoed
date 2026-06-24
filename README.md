# VideoReel Generator

**Intelligent video segment extraction for creating short-form reels from long-form content**

## Overview

VideoReel Generator is a Python utility that analyzes long-form videos (30 minutes to 2+ hours), identifies interesting segments with movement and activity, and extracts them as 20-second reels suitable for social media platforms.

## Status

🔬 **Research Phase Complete** - Ready for prototyping

## Key Features (Planned)

- **Intelligent Scene Detection** - Automatically identifies scene boundaries
- **Motion Analysis** - Scores segments based on movement intensity
- **Activity Recognition** - Optional ML-based object detection for interest scoring
- **Quality Preservation** - Extracts segments without quality loss (codec copying)
- **Configurable Scoring** - Customize what makes a segment "interesting"
- **Batch Processing** - Process multiple videos efficiently

## Architecture

### Pipeline Overview

```
Input Video (30min-2hr)
    ↓
Scene Detection (PySceneDetect)
    ↓
Interest Scoring (OpenCV + Optional YOLO)
    ↓
Scene Ranking & Selection
    ↓
Segment Extraction (PyAV/FFmpeg)
    ↓
Output: Top N interesting 20-second reels
```

### Technology Stack

#### Core Dependencies (Python 3.10+)

**Recommended Stack:**
- **PyAV (v17.1.0)** - Video processing with direct FFmpeg bindings
- **PySceneDetect (v0.7)** - Intelligent scene detection
- **OpenCV (v4.13+)** - Motion detection and frame analysis
- **NumPy** - Numerical computations

**Optional Enhancement:**
- **Ultralytics YOLO (v8.4+)** - ML-based object detection (requires GPU)
- **PyTorch** - Deep learning backend for YOLO

**Why This Stack:**
- All actively maintained (2025-2026 updates)
- Excellent performance on long videos
- Quality preservation capabilities
- GPU acceleration available but not required

### Interest Scoring Methodology

The system uses a composite scoring function combining multiple metrics:

**Traditional CV Metrics (No GPU Required):**
1. **Motion Magnitude** (40% weight) - Optical flow analysis
2. **Visual Complexity** (30% weight) - Edge density via Canny detection
3. **Color Variance** (10% weight) - HSV color distribution

**ML Metrics (GPU Recommended):**
4. **Object Count** (20% weight) - Number of detected objects
5. **Object Diversity** (10% weight) - Unique object classes

Weights are configurable based on your content type.

## Installation

### Prerequisites

- Python 3.10 or higher
- FFmpeg installed on system

#### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Basic Setup (CPU Only)

```bash
# Clone repository
git clone <repo-url>
cd videoed

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install core dependencies
pip install opencv-python scenedetect av numpy
```

### Full Setup (GPU-Enhanced)

```bash
# Install all dependencies
pip install opencv-python scenedetect av numpy ultralytics torch

# For NVIDIA CUDA support:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Verify GPU access
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Usage

### Basic Usage (Coming Soon)

```python
from videoreel import ReelGenerator

# Initialize generator
generator = ReelGenerator(
    motion_weight=0.4,
    complexity_weight=0.3,
    use_ml=False  # Set True for YOLO object detection
)

# Process video
reels = generator.extract_reels(
    input_path='long_video.mp4',
    output_dir='reels/',
    num_reels=10,
    segment_duration=20
)

# Results
for reel in reels:
    print(f"Extracted: {reel['path']} (score: {reel['score']:.2f})")
```

### Command-Line Interface (Coming Soon)

```bash
# Basic extraction
python -m videoreel extract long_video.mp4 --output reels/ --count 10

# With ML enhancement
python -m videoreel extract long_video.mp4 --output reels/ --count 10 --use-ml

# Custom scoring weights
python -m videoreel extract long_video.mp4 \
    --motion-weight 0.5 \
    --complexity-weight 0.3 \
    --object-weight 0.2

# Batch processing
python -m videoreel batch input_dir/ --output reels/ --count 5 --parallel 4
```

## Configuration

### Scoring Configuration (config.yaml - Coming Soon)

```yaml
# Interest scoring weights (must sum to 1.0)
scoring:
  motion_weight: 0.4
  complexity_weight: 0.3
  object_count_weight: 0.2
  object_diversity_weight: 0.1

# Scene detection settings
scene_detection:
  algorithm: content  # content, adaptive, or threshold
  threshold: 27.0
  min_scene_duration: 5  # seconds

# Extraction settings
extraction:
  segment_duration: 20  # seconds
  quality_preset: high  # high, medium, or fast
  codec_copy: true  # Use when possible for lossless extraction

# ML settings (if use_ml enabled)
ml:
  model: yolo26n.pt  # yolo26n, yolo26s, yolo26m, yolo26l, yolo26x
  confidence_threshold: 0.25
  device: cuda  # cuda or cpu
```

## Performance

### Expected Processing Times

**Test Case:** 60-minute 1080p video, 30fps

| Configuration | Hardware | Time | Quality |
|--------------|----------|------|---------|
| Traditional CV | 8-core CPU | 45-60 min | Good |
| ML-Enhanced | RTX 3060 GPU | 30-45 min | Excellent |
| ML-Enhanced | CPU only | 3-5 hours | Excellent |

### Optimization Tips

1. **Frame Sampling** - Process every Nth frame (configurable)
2. **Scene Pre-filtering** - Skip very short or very long scenes
3. **Early Termination** - Stop after finding desired number of segments
4. **Parallel Processing** - Multi-process scene analysis
5. **GPU Acceleration** - Use CUDA-enabled OpenCV + YOLO

## Development Roadmap

### Phase 1: Research ✅ (Complete)
- [x] Video processing library evaluation
- [x] Scene detection research
- [x] Motion detection techniques
- [x] Interest scoring methodology
- [x] Architecture design

### Phase 2: Prototype (Next)
- [ ] Development environment setup
- [ ] Core pipeline implementation
- [ ] Scene detection integration
- [ ] Motion scoring implementation
- [ ] Basic CLI interface
- [ ] Sample video testing

### Phase 3: Enhancement (Future)
- [ ] Audio overlay support
- [ ] Text/caption overlay
- [ ] Transition effects
- [ ] Web interface
- [ ] Batch processing optimization
- [ ] Configuration file support

### Phase 4: Production (Future)
- [ ] Error handling and validation
- [ ] Progress reporting
- [ ] Resume capability for interrupted processing
- [ ] Cloud deployment support
- [ ] API endpoint

## Technical Details

### Scene Detection Methods

**ContentDetector** (Recommended for most use cases)
- Analyzes HSV color space changes
- Fast processing
- Excellent for hard cuts

**AdaptiveDetector** (For camera motion)
- Two-pass rolling average
- Handles gradual transitions
- Better with moving camera

**ThresholdDetector** (For fades)
- RGB intensity analysis
- Detects fade in/out
- Complementary to other methods

### Motion Detection Approaches

**Optical Flow (Primary)**
- Dense Farneback algorithm
- Complete motion field analysis
- CPU: ~30ms/frame (1080p)
- GPU: ~5ms/frame (1080p with CUDA)

**Background Subtraction (Alternative)**
- MOG2 or KNN algorithms
- Best for static camera
- Real-time performance

### Quality Preservation

**Codec Copying (Lossless)**
```bash
ffmpeg -i input.mp4 -ss 60 -t 20 -c copy output.mp4
```
- No quality loss
- Fastest extraction
- Only works at keyframe boundaries

**High-Quality Re-encoding**
```bash
ffmpeg -i input.mp4 -ss 60 -t 20 -c:v libx264 -crf 18 -c:a copy output.mp4
```
- Minimal quality loss (visually lossless)
- Slower extraction
- Works at any timestamp

## Research Documentation

For detailed research findings, see:
- **[RESEARCH.md](RESEARCH.md)** - Comprehensive library analysis and technical research
- **[.claude/plans/VideoReel-Generator/current_plan.md](.claude/plans/VideoReel-Generator/current_plan.md)** - Project plan and task tracking

## Contributing

This project is currently in the research/prototyping phase. Contributions welcome once core implementation is complete.

## License

TBD

## References

### Key Libraries
- [PyAV](https://github.com/PyAV-Org/PyAV) - Pythonic bindings for FFmpeg
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) - Video scene detection
- [OpenCV](https://github.com/opencv/opencv) - Computer vision library
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - Object detection

### Documentation
- [PyAV Docs](https://pyav.org/docs/stable/)
- [PySceneDetect Docs](https://scenedetect.com)
- [OpenCV Docs](https://docs.opencv.org/4.x/)
- [Ultralytics Docs](https://docs.ultralytics.com/)

---

**Project Status:** Research Complete | Prototyping Next  
**Last Updated:** 2026-06-24  
**Python Version:** 3.10+

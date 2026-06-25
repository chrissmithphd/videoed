#!/usr/bin/env python3
"""
Extract interesting segments from video (NO music, NO rotation changes).

Usage:
    python3 extract_segments.py input.mp4 --output-dir segments/ -n 5

Features:
    - Analyzes video for motion, complexity, color
    - Finds top N interesting segments
    - Extracts to separate files
    - PRESERVES original orientation (no rotation changes)
    - PRESERVES original audio (no audio changes)
    - Uses FFmpeg -c copy for fast, lossless extraction
"""

import av
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict
import argparse
import subprocess


class BRollAnalyzer:
    """Analyzes video for interesting content."""

    def __init__(self):
        self.motion_weight = 0.25
        self.complexity_weight = 0.35
        self.stability_weight = 0.25
        self.color_weight = 0.15

    def analyze_frame_pair(self, prev_frame, curr_frame) -> Dict[str, float]:
        """Calculate interest metrics between two frames."""
        scores = {}

        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        # Motion score
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        avg_motion = np.mean(magnitude)
        scores['motion'] = self._score_motion(avg_motion)

        # Stability score
        motion_variance = np.std(magnitude)
        scores['stability'] = 1.0 / (1.0 + motion_variance / 10.0)

        # Visual complexity
        edges = cv2.Canny(curr_gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        scores['complexity'] = min(edge_density * 10, 1.0)

        # Color richness
        hsv = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        avg_saturation = np.mean(saturation) / 255.0
        color_variance = np.std(hsv) / 255.0
        scores['color'] = (avg_saturation * 0.6 + color_variance * 0.4)

        return scores

    def _score_motion(self, motion: float) -> float:
        """Score motion (prefer moderate motion)."""
        if motion < 1.0:
            return motion * 0.3
        elif motion < 3.0:
            return 0.6 + (motion - 1.0) / 2.0 * 0.3
        elif motion < 8.0:
            return 0.9 + (motion - 3.0) / 5.0 * 0.1
        elif motion < 15.0:
            return 1.0 - (motion - 8.0) / 7.0 * 0.3
        else:
            return max(0.7 - (motion - 15.0) / 20.0, 0.2)

    def composite_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted composite score."""
        return (
            scores.get('motion', 0) * self.motion_weight +
            scores.get('complexity', 0) * self.complexity_weight +
            scores.get('stability', 0) * self.stability_weight +
            scores.get('color', 0) * self.color_weight
        )


class SegmentExtractor:
    """Extract interesting segments from video."""

    def __init__(self, min_duration=10, max_duration=30, target_duration=20, sample_rate=5):
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.target_duration = target_duration
        self.sample_rate = sample_rate
        self.analyzer = BRollAnalyzer()

    def get_video_info(self, video_path: str) -> Dict:
        """Extract video metadata."""
        container = av.open(video_path)
        video_stream = container.streams.video[0]

        info = {
            'duration': float(video_stream.duration * video_stream.time_base),
            'fps': float(video_stream.average_rate),
            'width': video_stream.width,
            'height': video_stream.height,
            'total_frames': video_stream.frames,
        }

        container.close()
        return info

    def analyze_video(self, video_path: str) -> List[Dict]:
        """Analyze video and score segments."""
        print(f"\nAnalyzing: {Path(video_path).name}")

        container = av.open(video_path)
        info = self.get_video_info(video_path)
        fps = info['fps']
        duration = info['duration']

        print(f"Duration: {duration:.1f}s | FPS: {fps:.1f} | "
              f"Resolution: {info['width']}x{info['height']}")

        frame_scores = []
        prev_frame = None
        frame_idx = 0

        total_frames = int(duration * fps)
        pbar = tqdm(total=total_frames, desc="Processing frames", unit="frame")

        try:
            for frame in container.decode(video=0):
                if frame_idx % self.sample_rate != 0:
                    frame_idx += 1
                    pbar.update(1)
                    continue

                img = frame.to_ndarray(format='bgr24')
                timestamp = float(frame.time)

                if prev_frame is not None:
                    scores = self.analyzer.analyze_frame_pair(prev_frame, img)
                    composite = self.analyzer.composite_score(scores)

                    frame_scores.append({
                        'frame_idx': frame_idx,
                        'timestamp': timestamp,
                        'scores': scores,
                        'composite': composite
                    })

                prev_frame = img
                frame_idx += 1
                pbar.update(1)

        finally:
            pbar.close()
            container.close()

        print(f"Analyzed {len(frame_scores)} frame pairs")

        segments = self._find_best_segments(frame_scores, self.target_duration, fps)
        return segments

    def _find_best_segments(self, frame_scores: List[Dict],
                           window_duration: float, fps: float) -> List[Dict]:
        """Find best segments using sliding window."""
        if not frame_scores:
            return []

        window_frames = int(window_duration * fps / self.sample_rate)
        step_frames = max(int(fps / self.sample_rate), 1)

        segments = []

        for i in range(0, len(frame_scores) - window_frames, step_frames):
            window = frame_scores[i:i + window_frames]
            avg_score = np.mean([f['composite'] for f in window])

            start_time = window[0]['timestamp']
            end_time = window[-1]['timestamp']
            duration = end_time - start_time

            if duration < self.min_duration:
                continue

            segments.append({
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'score': avg_score,
            })

        segments.sort(key=lambda x: x['score'], reverse=True)
        filtered = self._remove_overlaps(segments)
        return filtered

    def _remove_overlaps(self, segments: List[Dict], min_gap: float = 5.0) -> List[Dict]:
        """Remove overlapping segments."""
        if not segments:
            return []

        result = [segments[0]]

        for segment in segments[1:]:
            overlap = False
            for selected in result:
                if not (segment['end_time'] < selected['start_time'] - min_gap or
                       segment['start_time'] > selected['end_time'] + min_gap):
                    overlap = True
                    break

            if not overlap:
                result.append(segment)

        return result

    def extract_segment(self, video_path: str, segment: Dict, output_path: Path, segment_num: int):
        """Extract segment using FFmpeg (preserves orientation and audio)."""
        start_time = segment['start_time']
        duration = min(segment['duration'], self.max_duration)

        # Use FFmpeg with codec copy (no re-encoding)
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start_time),
            '-i', str(video_path),
            '-t', str(duration),
            '-c', 'copy',  # Copy all streams (video + audio)
            str(output_path)
        ]

        print(f"  Extracting segment {segment_num}: {start_time:.1f}s - {start_time+duration:.1f}s")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"  ERROR: {result.stderr}")
            raise RuntimeError(f"FFmpeg failed for segment {segment_num}")

        print(f"    ✓ Created: {output_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract interesting segments from video (no modifications)'
    )
    parser.add_argument('input', help='Input video file')
    parser.add_argument('--output-dir', required=True, help='Output directory')
    parser.add_argument('-n', '--num-segments', type=int, default=5,
                       help='Number of segments to extract (default: 5)')
    parser.add_argument('--min-duration', type=int, default=10,
                       help='Min segment duration in seconds (default: 10)')
    parser.add_argument('--max-duration', type=int, default=30,
                       help='Max segment duration in seconds (default: 30)')
    parser.add_argument('--target-duration', type=int, default=20,
                       help='Target segment duration in seconds (default: 20)')
    parser.add_argument('--sample-rate', type=int, default=5,
                       help='Process every Nth frame (default: 5)')

    args = parser.parse_args()

    video_path = Path(args.input)
    if not video_path.exists():
        print(f"ERROR: File not found: {video_path}")
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract and analyze
    extractor = SegmentExtractor(
        min_duration=args.min_duration,
        max_duration=args.max_duration,
        target_duration=args.target_duration,
        sample_rate=args.sample_rate
    )

    segments = extractor.analyze_video(str(video_path))

    if not segments:
        print(f"No suitable segments found")
        return 1

    print(f"\nFound {len(segments)} candidate segments")
    print(f"Extracting top {min(args.num_segments, len(segments))} segments:\n")

    # Extract segments
    for i, seg in enumerate(segments[:args.num_segments], 1):
        output_path = output_dir / f"{video_path.stem}_segment_{i:02d}.mp4"
        print(f"{i}. Score: {seg['score']:.3f}")

        try:
            extractor.extract_segment(str(video_path), seg, output_path, i)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    print(f"\nDone! Check {output_dir}/")
    return 0


if __name__ == '__main__':
    exit(main())

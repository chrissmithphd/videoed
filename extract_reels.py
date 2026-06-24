#!/usr/bin/env python3
"""
VideoReel Generator - Prototype
Extracts interesting segments from B-roll footage
"""

import av
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json
from typing import List, Dict, Tuple
import argparse


class BRollAnalyzer:
    """Analyzes video for B-roll specific interest metrics"""

    def __init__(self,
                 motion_weight=0.25,      # Lower for B-roll (smooth over action)
                 complexity_weight=0.35,   # Higher - visual richness important
                 stability_weight=0.25,    # Penalize shakiness in B-roll
                 color_weight=0.15):       # Color variance/saturation
        self.motion_weight = motion_weight
        self.complexity_weight = complexity_weight
        self.stability_weight = stability_weight
        self.color_weight = color_weight

    def analyze_frame_pair(self, prev_frame, curr_frame) -> Dict[str, float]:
        """Calculate interest metrics between two frames"""
        scores = {}

        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        # Motion score (moderate motion preferred for B-roll)
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)

        # For B-roll, prefer moderate motion (not too fast, not static)
        avg_motion = np.mean(magnitude)
        # Optimal B-roll motion is around 2-8 pixels/frame
        scores['motion'] = self._score_motion_for_broll(avg_motion)

        # Stability score (penalize shaky footage)
        # High variance in motion vectors = unstable/shaky
        motion_variance = np.std(magnitude)
        scores['stability'] = 1.0 / (1.0 + motion_variance / 10.0)

        # Visual complexity (edge density)
        edges = cv2.Canny(curr_gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        scores['complexity'] = min(edge_density * 10, 1.0)  # Normalize

        # Color richness (saturation and variance)
        hsv = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        avg_saturation = np.mean(saturation) / 255.0
        color_variance = np.std(hsv) / 255.0
        scores['color'] = (avg_saturation * 0.6 + color_variance * 0.4)

        return scores

    def _score_motion_for_broll(self, motion: float) -> float:
        """
        Score motion specifically for B-roll footage.
        Optimal range: 2-8 pixels/frame
        Too low = static/boring, too high = chaotic
        """
        if motion < 1.0:
            # Very static - low score
            return motion * 0.3
        elif motion < 3.0:
            # Gentle motion - good for B-roll
            return 0.6 + (motion - 1.0) / 2.0 * 0.3
        elif motion < 8.0:
            # Ideal B-roll motion
            return 0.9 + (motion - 3.0) / 5.0 * 0.1  # 0.9-1.0
        elif motion < 15.0:
            # Getting too fast, but still usable
            return 1.0 - (motion - 8.0) / 7.0 * 0.3  # 1.0-0.7
        else:
            # Too chaotic for B-roll
            return max(0.7 - (motion - 15.0) / 20.0, 0.2)

    def composite_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted composite score"""
        return (
            scores.get('motion', 0) * self.motion_weight +
            scores.get('complexity', 0) * self.complexity_weight +
            scores.get('stability', 0) * self.stability_weight +
            scores.get('color', 0) * self.color_weight
        )


class ReelExtractor:
    """Main class for extracting reels from video"""

    def __init__(self,
                 min_duration=10,
                 max_duration=30,
                 target_duration=20,
                 sample_rate=5):  # Process every Nth frame
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.target_duration = target_duration
        self.sample_rate = sample_rate
        self.analyzer = BRollAnalyzer()

    def get_video_info(self, video_path: str) -> Dict:
        """Extract video metadata"""
        container = av.open(video_path)
        video_stream = container.streams.video[0]

        info = {
            'duration': float(video_stream.duration * video_stream.time_base),
            'fps': float(video_stream.average_rate),
            'width': video_stream.width,
            'height': video_stream.height,
            'codec': video_stream.codec_context.name,
            'total_frames': video_stream.frames
        }

        container.close()
        return info

    def analyze_video(self, video_path: str) -> List[Dict]:
        """
        Analyze entire video and score segments.
        Returns list of candidate segments with scores.
        """
        print(f"\nAnalyzing: {Path(video_path).name}")

        container = av.open(video_path)
        video_stream = container.streams.video[0]

        info = self.get_video_info(video_path)
        fps = info['fps']
        duration = info['duration']

        print(f"Duration: {duration:.1f}s | FPS: {fps:.1f} | Resolution: {info['width']}x{info['height']}")

        # Sliding window analysis
        window_duration = self.target_duration
        window_frames = int(window_duration * fps)
        step_frames = int(fps * 2)  # Move window by 2 seconds

        segments = []
        frame_scores = []

        prev_frame = None
        frame_idx = 0

        # Calculate total frames for progress bar
        total_frames = int(duration * fps)
        pbar = tqdm(total=total_frames, desc="Processing frames", unit="frame")

        try:
            for frame in container.decode(video=0):
                # Sample frames to speed up processing
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

        # Find best segments using sliding window
        segments = self._find_best_segments(frame_scores, window_duration, fps)

        return segments

    def _find_best_segments(self, frame_scores: List[Dict],
                           window_duration: float, fps: float) -> List[Dict]:
        """
        Find best segments using sliding window approach.
        """
        if not frame_scores:
            return []

        window_frames = int(window_duration * fps / self.sample_rate)  # Account for sampling
        step_frames = max(int(fps / self.sample_rate), 1)  # 1 second steps

        segments = []

        for i in range(0, len(frame_scores) - window_frames, step_frames):
            window = frame_scores[i:i + window_frames]

            # Calculate average score for this window
            avg_score = np.mean([f['composite'] for f in window])

            # Get time bounds
            start_time = window[0]['timestamp']
            end_time = window[-1]['timestamp']
            duration = end_time - start_time

            # Ensure minimum duration
            if duration < self.min_duration:
                continue

            segments.append({
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'score': avg_score,
                'frame_start': window[0]['frame_idx'],
                'frame_end': window[-1]['frame_idx']
            })

        # Sort by score
        segments.sort(key=lambda x: x['score'], reverse=True)

        # Remove overlapping segments (keep highest scoring)
        filtered = self._remove_overlaps(segments)

        return filtered

    def _remove_overlaps(self, segments: List[Dict],
                        min_gap: float = 5.0) -> List[Dict]:
        """
        Remove overlapping segments, keeping highest scores.
        Ensure minimum gap between segments.
        """
        if not segments:
            return []

        result = [segments[0]]

        for segment in segments[1:]:
            # Check if this segment overlaps with any already selected
            overlap = False
            for selected in result:
                # Check for overlap or too-close proximity
                if not (segment['end_time'] < selected['start_time'] - min_gap or
                       segment['start_time'] > selected['end_time'] + min_gap):
                    overlap = True
                    break

            if not overlap:
                result.append(segment)

        return result

    def extract_segments(self, video_path: str, segments: List[Dict],
                        output_dir: Path):
        """
        Extract video segments using PyAV (high quality).
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        video_name = Path(video_path).stem

        print(f"\nExtracting {len(segments)} segments...")

        for idx, segment in enumerate(segments):
            output_path = output_dir / f"{video_name}_reel_{idx+1:02d}_score{segment['score']:.2f}.mp4"

            try:
                self._extract_segment(
                    video_path,
                    segment['start_time'],
                    segment['end_time'],
                    output_path
                )
                print(f"✓ Extracted: {output_path.name} ({segment['duration']:.1f}s, score: {segment['score']:.3f})")
            except Exception as e:
                print(f"✗ Failed to extract segment {idx+1}: {e}")

    def _extract_segment(self, input_path: str, start_time: float,
                        end_time: float, output_path: Path):
        """
        Extract a single segment with re-encoding for quality.
        """
        input_container = av.open(input_path)
        output_container = av.open(str(output_path), 'w')

        try:
            # Get input stream
            input_stream = input_container.streams.video[0]

            # Create output stream with same codec settings
            output_stream = output_container.add_stream('libx264', rate=input_stream.average_rate)
            output_stream.width = input_stream.width
            output_stream.height = input_stream.height
            output_stream.pix_fmt = 'yuv420p'
            output_stream.options = {'crf': '18', 'preset': 'medium'}

            # Seek to start
            seek_point = int(start_time * av.time_base)
            input_container.seek(seek_point)

            # Copy audio stream if present
            audio_stream = None
            output_audio_stream = None
            if input_container.streams.audio:
                audio_stream = input_container.streams.audio[0]
                output_audio_stream = output_container.add_stream(
                    audio_stream.codec_context.name,
                    rate=audio_stream.rate
                )

            # Decode and encode frames
            for packet in input_container.demux(video=0, audio=0 if audio_stream else None):
                if packet.stream.type == 'video':
                    for frame in packet.decode():
                        if frame.time < start_time:
                            continue
                        if frame.time > end_time:
                            break

                        # Re-encode frame
                        new_packets = output_stream.encode(frame)
                        for new_packet in new_packets:
                            output_container.mux(new_packet)

                        if frame.time >= end_time:
                            break

                elif packet.stream.type == 'audio' and output_audio_stream:
                    for frame in packet.decode():
                        if frame.time < start_time:
                            continue
                        if frame.time > end_time:
                            break

                        new_packets = output_audio_stream.encode(frame)
                        for new_packet in new_packets:
                            output_container.mux(new_packet)

                if packet.pts * packet.time_base > end_time:
                    break

            # Flush encoders
            for packet in output_stream.encode(None):
                output_container.mux(packet)

            if output_audio_stream:
                for packet in output_audio_stream.encode(None):
                    output_container.mux(packet)

        finally:
            input_container.close()
            output_container.close()


def main():
    parser = argparse.ArgumentParser(
        description='Extract interesting reels from B-roll footage'
    )
    parser.add_argument('input', nargs='+', help='Input video file(s)')
    parser.add_argument('-o', '--output', default='reels',
                       help='Output directory (default: reels/)')
    parser.add_argument('-n', '--num-reels', type=int, default=5,
                       help='Number of reels to extract per video (default: 5)')
    parser.add_argument('--min-duration', type=int, default=10,
                       help='Minimum reel duration in seconds (default: 10)')
    parser.add_argument('--max-duration', type=int, default=30,
                       help='Maximum reel duration in seconds (default: 30)')
    parser.add_argument('--target-duration', type=int, default=20,
                       help='Target reel duration in seconds (default: 20)')
    parser.add_argument('--sample-rate', type=int, default=5,
                       help='Process every Nth frame (default: 5, higher=faster)')
    parser.add_argument('--save-analysis', action='store_true',
                       help='Save analysis JSON for each video')

    args = parser.parse_args()

    output_dir = Path(args.output)

    extractor = ReelExtractor(
        min_duration=args.min_duration,
        max_duration=args.max_duration,
        target_duration=args.target_duration,
        sample_rate=args.sample_rate
    )

    for video_path in args.input:
        if not Path(video_path).exists():
            print(f"Error: File not found: {video_path}")
            continue

        # Get video info
        info = extractor.get_video_info(video_path)

        # Analyze video
        segments = extractor.analyze_video(video_path)

        if not segments:
            print(f"No suitable segments found in {video_path}")
            continue

        print(f"\nFound {len(segments)} candidate segments")
        print(f"Top {min(args.num_reels, len(segments))} segments:")
        for i, seg in enumerate(segments[:args.num_reels]):
            print(f"  {i+1}. {seg['start_time']:.1f}s - {seg['end_time']:.1f}s "
                  f"(score: {seg['score']:.3f})")

        # Save analysis if requested
        if args.save_analysis:
            analysis_path = output_dir / f"{Path(video_path).stem}_analysis.json"
            analysis_path.parent.mkdir(parents=True, exist_ok=True)
            with open(analysis_path, 'w') as f:
                json.dump({
                    'video_info': info,
                    'segments': segments[:args.num_reels]
                }, f, indent=2)
            print(f"Saved analysis to: {analysis_path}")

        # Extract segments
        extractor.extract_segments(
            video_path,
            segments[:args.num_reels],
            output_dir
        )

    print(f"\n✓ Complete! Reels saved to: {output_dir}/")


if __name__ == '__main__':
    main()

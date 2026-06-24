#!/usr/bin/env python3
"""
VideoReel Generator - WITH MUSIC
Extracts interesting segments and adds background music using FFmpeg
"""

import av
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json
from typing import List, Dict, Tuple, Optional
import argparse
import subprocess
import random


def get_rotation(container) -> int:
    """
    Extract rotation from video stream side data.
    Returns rotation in degrees (0, 90, 180, or 270)
    """
    for stream in container.streams.video:
        for frame in container.decode(video=0):
            if frame.side_data:
                for side_data in frame.side_data:
                    if 'DISPLAYMATRIX' in str(side_data.type):
                        print(f"  Found rotation metadata: {side_data}")
                        return 90
            break
        break
    return 0


def rotate_frame(frame_array: np.ndarray, rotation: int) -> np.ndarray:
    """Rotate frame by specified degrees."""
    if rotation == 0:
        return frame_array
    elif rotation == 90:
        return cv2.rotate(frame_array, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif rotation == 180:
        return cv2.rotate(frame_array, cv2.ROTATE_180)
    elif rotation == 270:
        return cv2.rotate(frame_array, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        print(f"Warning: Unsupported rotation {rotation}°, not rotating")
        return frame_array


class BRollAnalyzer:
    """Analyzes video for B-roll specific interest metrics"""

    def __init__(self,
                 motion_weight=0.25,
                 complexity_weight=0.35,
                 stability_weight=0.25,
                 color_weight=0.15):
        self.motion_weight = motion_weight
        self.complexity_weight = complexity_weight
        self.stability_weight = stability_weight
        self.color_weight = color_weight

    def analyze_frame_pair(self, prev_frame, curr_frame) -> Dict[str, float]:
        """Calculate interest metrics between two frames"""
        scores = {}

        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        avg_motion = np.mean(magnitude)
        scores['motion'] = self._score_motion_for_broll(avg_motion)

        motion_variance = np.std(magnitude)
        scores['stability'] = 1.0 / (1.0 + motion_variance / 10.0)

        edges = cv2.Canny(curr_gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        scores['complexity'] = min(edge_density * 10, 1.0)

        hsv = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        avg_saturation = np.mean(saturation) / 255.0
        color_variance = np.std(hsv) / 255.0
        scores['color'] = (avg_saturation * 0.6 + color_variance * 0.4)

        return scores

    def _score_motion_for_broll(self, motion: float) -> float:
        """Score motion for B-roll (prefer moderate motion)"""
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
                 sample_rate=5,
                 music_dir: Optional[Path] = None,
                 music_volume: float = 0.3):
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.target_duration = target_duration
        self.sample_rate = sample_rate
        self.analyzer = BRollAnalyzer()
        self.music_dir = music_dir
        self.music_volume = music_volume

    def get_video_info(self, video_path: str) -> Dict:
        """Extract video metadata including rotation"""
        container = av.open(video_path)
        video_stream = container.streams.video[0]

        rotation = get_rotation(container)

        info = {
            'duration': float(video_stream.duration * video_stream.time_base),
            'fps': float(video_stream.average_rate),
            'width': video_stream.width,
            'height': video_stream.height,
            'codec': video_stream.codec_context.name,
            'total_frames': video_stream.frames,
            'rotation': rotation
        }

        container.close()
        return info

    def analyze_video(self, video_path: str) -> Tuple[List[Dict], int]:
        """Analyze video and score segments. Returns (segments, rotation)"""
        print(f"\nAnalyzing: {Path(video_path).name}")

        container = av.open(video_path)

        info = self.get_video_info(video_path)
        fps = info['fps']
        duration = info['duration']
        rotation = info['rotation']

        print(f"Duration: {duration:.1f}s | FPS: {fps:.1f} | "
              f"Resolution: {info['width']}x{info['height']}")
        if rotation:
            print(f"Rotation: {rotation}° (will be corrected in output)")

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

                if rotation:
                    img = rotate_frame(img, rotation)

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
        return segments, rotation

    def _find_best_segments(self, frame_scores: List[Dict],
                           window_duration: float, fps: float) -> List[Dict]:
        """Find best segments using sliding window"""
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
                'frame_start': window[0]['frame_idx'],
                'frame_end': window[-1]['frame_idx']
            })

        segments.sort(key=lambda x: x['score'], reverse=True)
        filtered = self._remove_overlaps(segments)
        return filtered

    def _remove_overlaps(self, segments: List[Dict], min_gap: float = 5.0) -> List[Dict]:
        """Remove overlapping segments"""
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

    def _get_music_files(self) -> List[Path]:
        """Get list of available music files"""
        if not self.music_dir or not self.music_dir.exists():
            return []

        music_files = []
        for ext in ['*.mp3', '*.wav', '*.ogg', '*.m4a']:
            music_files.extend(self.music_dir.glob(ext))

        return sorted(music_files)

    def extract_segments(self, video_path: str, segments: List[Dict],
                        output_dir: Path, rotation: int = 0):
        """Extract video segments with rotation correction and music"""
        output_dir.mkdir(parents=True, exist_ok=True)
        video_name = Path(video_path).stem

        music_files = self._get_music_files()
        if music_files:
            print(f"\nFound {len(music_files)} music track(s)")
        else:
            print(f"\nNo music found in {self.music_dir}, extracting without audio")

        print(f"Extracting {len(segments)} segments...")
        if rotation:
            print(f"  Correcting rotation: {rotation}°")

        for idx, segment in enumerate(segments):
            output_path = output_dir / f"{video_name}_reel_{idx+1:02d}_score{segment['score']:.2f}.mp4"

            music_file = random.choice(music_files) if music_files else None

            try:
                self._extract_segment_ffmpeg(
                    video_path,
                    segment['start_time'],
                    segment['duration'],
                    output_path,
                    rotation,
                    music_file
                )
                music_name = music_file.stem if music_file else "no audio"
                print(f"✓ {output_path.name} ({segment['duration']:.1f}s, "
                      f"score: {segment['score']:.3f}, music: {music_name})")
            except Exception as e:
                print(f"✗ Failed segment {idx+1}: {e}")

    def _extract_segment_ffmpeg(self, input_path: str, start_time: float,
                                duration: float, output_path: Path,
                                rotation: int = 0, music_file: Optional[Path] = None):
        """Extract segment using FFmpeg with music replacement"""

        cmd = [
            'ffmpeg',
            '-y',
            '-ss', str(start_time),
            '-i', input_path,
        ]

        if music_file:
            cmd.extend([
                '-stream_loop', '-1',
                '-i', str(music_file),
            ])

        cmd.extend(['-t', str(duration)])

        vf_filters = []
        if rotation == 90:
            vf_filters.append('transpose=2')
        elif rotation == 180:
            vf_filters.append('transpose=2,transpose=2')
        elif rotation == 270:
            vf_filters.append('transpose=1')

        if vf_filters:
            cmd.extend(['-vf', ','.join(vf_filters)])

        cmd.extend([
            '-c:v', 'libx264',
            '-crf', '18',
            '-preset', 'medium',
        ])

        if music_file:
            cmd.extend([
                '-c:a', 'aac',
                '-b:a', '192k',
                '-filter:a', f'volume={self.music_volume}',
                '-shortest',
                '-map', '0:v:0',
                '-map', '1:a:0',
            ])
        else:
            cmd.extend(['-an'])

        cmd.append(str(output_path))

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract interesting reels with background music'
    )
    parser.add_argument('input', nargs='+', help='Input video file(s)')
    parser.add_argument('-o', '--output', default='reels',
                       help='Output directory (default: reels/)')
    parser.add_argument('-n', '--num-reels', type=int, default=5,
                       help='Number of reels per video (default: 5)')
    parser.add_argument('--min-duration', type=int, default=10,
                       help='Min reel duration in seconds (default: 10)')
    parser.add_argument('--max-duration', type=int, default=30,
                       help='Max reel duration in seconds (default: 30)')
    parser.add_argument('--target-duration', type=int, default=20,
                       help='Target reel duration in seconds (default: 20)')
    parser.add_argument('--sample-rate', type=int, default=5,
                       help='Process every Nth frame (default: 5)')
    parser.add_argument('--music-dir', type=Path, default=Path('music/viral'),
                       help='Directory with music files (default: music/viral/)')
    parser.add_argument('--music-volume', type=float, default=0.3,
                       help='Music volume (0.0-1.0, default: 0.3)')
    parser.add_argument('--save-analysis', action='store_true',
                       help='Save analysis JSON')

    args = parser.parse_args()

    output_dir = Path(args.output)

    extractor = ReelExtractor(
        min_duration=args.min_duration,
        max_duration=args.max_duration,
        target_duration=args.target_duration,
        sample_rate=args.sample_rate,
        music_dir=args.music_dir,
        music_volume=args.music_volume
    )

    for video_path in args.input:
        if not Path(video_path).exists():
            print(f"Error: File not found: {video_path}")
            continue

        info = extractor.get_video_info(video_path)
        segments, rotation = extractor.analyze_video(video_path)

        if not segments:
            print(f"No suitable segments found in {video_path}")
            continue

        print(f"\nFound {len(segments)} candidate segments")
        print(f"Top {min(args.num_reels, len(segments))} segments:")
        for i, seg in enumerate(segments[:args.num_reels]):
            print(f"  {i+1}. {seg['start_time']:.1f}s - {seg['end_time']:.1f}s "
                  f"(score: {seg['score']:.3f})")

        if args.save_analysis:
            analysis_path = output_dir / f"{Path(video_path).stem}_analysis.json"
            analysis_path.parent.mkdir(parents=True, exist_ok=True)
            with open(analysis_path, 'w') as f:
                json.dump({
                    'video_info': info,
                    'segments': segments[:args.num_reels],
                    'rotation_corrected': rotation
                }, f, indent=2)
            print(f"Saved analysis to: {analysis_path}")

        extractor.extract_segments(
            video_path,
            segments[:args.num_reels],
            output_dir,
            rotation=rotation
        )

    print(f"\n✓ Complete! Reels saved to: {output_dir}/")


if __name__ == '__main__':
    main()

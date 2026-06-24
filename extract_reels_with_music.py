#!/usr/bin/env python3
"""
VideoReel Generator - With Music Overlay
Extracts interesting segments from B-roll footage and adds background music
"""

import av
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json
from typing import List, Dict, Optional
import argparse
import random
import sys

# Optional MoviePy for music overlay
try:
    from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("Warning: MoviePy not installed. Music overlay disabled.")
    print("Install with: pip install moviepy")

# Optional Pydub for audio preprocessing
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


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

        # Motion score
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        avg_motion = np.mean(magnitude)
        scores['motion'] = self._score_motion_for_broll(avg_motion)

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


class MusicOverlay:
    """Handles background music overlay on video"""

    def __init__(self, music_dir: Optional[str] = None):
        if not MOVIEPY_AVAILABLE:
            raise RuntimeError("MoviePy not installed. Cannot add music.")

        self.music_dir = Path(music_dir) if music_dir else None
        self.available_tracks = []

        if self.music_dir and self.music_dir.exists():
            self.available_tracks = list(self.music_dir.glob('*.mp3')) + \
                                   list(self.music_dir.glob('*.wav'))
            print(f"Found {len(self.available_tracks)} music tracks in {music_dir}")

    def select_random_track(self) -> Optional[Path]:
        """Select random music track"""
        if not self.available_tracks:
            return None
        return random.choice(self.available_tracks)

    def add_music(self,
                  video_path: Path,
                  output_path: Path,
                  music_path: Optional[Path] = None,
                  volume: float = 0.35,
                  fade_duration: float = 2.0,
                  normalize: bool = True):
        """
        Add background music to video.

        Args:
            video_path: Input video file
            output_path: Output video file
            music_path: Specific music file (or None for random)
            volume: Music volume (0.0-1.0)
            fade_duration: Fade duration in seconds
            normalize: Normalize audio levels
        """
        if music_path is None:
            music_path = self.select_random_track()

        if music_path is None:
            raise ValueError("No music file specified and no tracks available")

        print(f"  Adding music: {music_path.name}")

        # Load video
        video = VideoFileClip(str(video_path))
        video_duration = video.duration

        # Preprocess with Pydub if available
        temp_music = None
        if normalize and PYDUB_AVAILABLE:
            try:
                audio_seg = AudioSegment.from_file(str(music_path))
                audio_seg = audio_seg.normalize()

                # Loop or trim
                target_ms = int(video_duration * 1000)
                if len(audio_seg) < target_ms:
                    loops = (target_ms // len(audio_seg)) + 1
                    audio_seg = (audio_seg * loops)[:target_ms]
                else:
                    audio_seg = audio_seg[:target_ms]

                temp_music = f"/tmp/music_{output_path.stem}.mp3"
                audio_seg.export(temp_music, format="mp3")
                music_path = temp_music
            except Exception as e:
                print(f"  Warning: Pydub processing failed: {e}")

        # Load music
        music = AudioFileClip(str(music_path))

        # Apply volume and fades
        music = (music
            .with_duration(video_duration)
            .with_volume_scaled(volume)
            .audio_fadein(fade_duration)
            .audio_fadeout(fade_duration))

        # Mix with original audio
        if video.audio:
            final_audio = CompositeAudioClip([video.audio, music])
        else:
            final_audio = music

        final = video.with_audio(final_audio)

        # Write output
        final.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            audio_bitrate='192k',
            preset='medium',
            ffmpeg_params=['-crf', '18'],
            logger=None  # Suppress moviepy output
        )

        # Cleanup
        video.close()
        music.close()

        if temp_music and Path(temp_music).exists():
            Path(temp_music).unlink()


class ReelExtractor:
    """Main class for extracting reels from video"""

    def __init__(self,
                 min_duration=10,
                 max_duration=30,
                 target_duration=20,
                 sample_rate=5):
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
        """Analyze video and score segments"""
        print(f"\nAnalyzing: {Path(video_path).name}")

        container = av.open(video_path)
        video_stream = container.streams.video[0]

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

    def extract_segments(self, video_path: str, segments: List[Dict],
                        output_dir: Path, add_music: bool = False,
                        music_overlay: Optional[MusicOverlay] = None):
        """Extract video segments"""
        output_dir.mkdir(parents=True, exist_ok=True)
        video_name = Path(video_path).stem

        print(f"\nExtracting {len(segments)} segments...")

        for idx, segment in enumerate(segments):
            base_name = f"{video_name}_reel_{idx+1:02d}_score{segment['score']:.2f}"
            temp_path = output_dir / f"{base_name}_temp.mp4"
            final_path = output_dir / f"{base_name}.mp4"

            try:
                # Extract segment
                self._extract_segment(
                    video_path,
                    segment['start_time'],
                    segment['end_time'],
                    temp_path if add_music else final_path
                )

                # Add music if requested
                if add_music and music_overlay and MOVIEPY_AVAILABLE:
                    music_overlay.add_music(temp_path, final_path)
                    temp_path.unlink()  # Remove temp file

                print(f"✓ {final_path.name} ({segment['duration']:.1f}s, "
                      f"score: {segment['score']:.3f})")

            except Exception as e:
                print(f"✗ Failed segment {idx+1}: {e}")

    def _extract_segment(self, input_path: str, start_time: float,
                        end_time: float, output_path: Path):
        """Extract a single segment"""
        input_container = av.open(input_path)
        output_container = av.open(str(output_path), 'w')

        try:
            input_stream = input_container.streams.video[0]

            output_stream = output_container.add_stream(
                'libx264',
                rate=input_stream.average_rate
            )
            output_stream.width = input_stream.width
            output_stream.height = input_stream.height
            output_stream.pix_fmt = 'yuv420p'
            output_stream.options = {'crf': '18', 'preset': 'medium'}

            seek_point = int(start_time * av.time_base)
            input_container.seek(seek_point)

            # Handle audio
            audio_stream = None
            output_audio_stream = None
            if input_container.streams.audio:
                audio_stream = input_container.streams.audio[0]
                output_audio_stream = output_container.add_stream(
                    audio_stream.codec_context.name,
                    rate=audio_stream.rate
                )

            # Encode frames
            for packet in input_container.demux(video=0, audio=0 if audio_stream else None):
                if packet.stream.type == 'video':
                    for frame in packet.decode():
                        if frame.time < start_time:
                            continue
                        if frame.time > end_time:
                            break

                        for new_packet in output_stream.encode(frame):
                            output_container.mux(new_packet)

                elif packet.stream.type == 'audio' and output_audio_stream:
                    for frame in packet.decode():
                        if frame.time < start_time:
                            continue
                        if frame.time > end_time:
                            break

                        for new_packet in output_audio_stream.encode(frame):
                            output_container.mux(new_packet)

                if packet.pts * packet.time_base > end_time:
                    break

            # Flush
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
        description='Extract interesting reels from B-roll footage with optional music'
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
    parser.add_argument('--save-analysis', action='store_true',
                       help='Save analysis JSON')
    parser.add_argument('--add-music', action='store_true',
                       help='Add background music to reels')
    parser.add_argument('--music-dir', type=str,
                       help='Directory containing music files')
    parser.add_argument('--music-volume', type=float, default=0.35,
                       help='Music volume 0.0-1.0 (default: 0.35)')
    parser.add_argument('--music-fade', type=float, default=2.0,
                       help='Music fade duration in seconds (default: 2.0)')

    args = parser.parse_args()

    # Check music requirements
    if args.add_music:
        if not MOVIEPY_AVAILABLE:
            print("Error: MoviePy required for music. Install: pip install moviepy")
            sys.exit(1)
        if not args.music_dir:
            print("Error: --music-dir required when using --add-music")
            sys.exit(1)

    output_dir = Path(args.output)

    # Initialize music overlay if needed
    music_overlay = None
    if args.add_music:
        music_overlay = MusicOverlay(args.music_dir)

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

        info = extractor.get_video_info(video_path)
        segments = extractor.analyze_video(video_path)

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
                    'segments': segments[:args.num_reels]
                }, f, indent=2)
            print(f"Saved analysis to: {analysis_path}")

        extractor.extract_segments(
            video_path,
            segments[:args.num_reels],
            output_dir,
            add_music=args.add_music,
            music_overlay=music_overlay
        )

    print(f"\n✓ Complete! Reels saved to: {output_dir}/")


if __name__ == '__main__':
    main()

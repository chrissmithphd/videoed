#!/usr/bin/env python3
"""
Video Text Overlay Tool - Production Ready

Adds text overlays to video files using FFmpeg drawtext filter.
This is the FASTEST approach for adding text to videos.

Features:
- Reads text from TextThoughts.txt (segments separated by --)
- Viral-style formatting (white text, black border, centered)
- Optional semi-transparent background box
- Word wrapping for multi-line text
- Single-pass FFmpeg encoding (fast)

Performance: ~1x realtime for 20-second clips (re-encode required for overlay)

Usage:
    python add_text_overlay.py input.mp4 output.mp4 --text-file TextThoughts.txt --segment 0
    python add_text_overlay.py input.mp4 output.mp4 --text "Custom text" --with-background
"""

import argparse
import subprocess
import textwrap
import sys
from pathlib import Path


class TextOverlayProcessor:
    """Handles text overlay on videos using FFmpeg."""

    def __init__(self, font_file=None, font_size=48, max_text_width=40):
        """
        Initialize text overlay processor.

        Args:
            font_file: Path to TTF font file (defaults to Liberation Sans Bold)
            font_size: Font size in pixels (default 48)
            max_text_width: Maximum characters per line for word wrap
        """
        self.font_file = font_file or self._find_best_font()
        self.font_size = font_size
        self.max_text_width = max_text_width

    def _find_best_font(self):
        """Find best available font for viral-style overlays."""
        # Priority: Impact > Arial Black > Liberation Sans Bold > DejaVu Sans Bold
        font_preferences = [
            "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]

        for font in font_preferences:
            if Path(font).exists():
                return font

        # Fallback - try to find any bold font
        try:
            result = subprocess.run(
                ["fc-list", ":style=Bold", "file"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout:
                first_font = result.stdout.split('\n')[0].split(':')[0].strip()
                if first_font:
                    return first_font
        except Exception:
            pass

        raise RuntimeError("No suitable font found. Install Liberation fonts: sudo apt-get install fonts-liberation")

    def read_text_segments(self, text_file):
        """
        Read text segments from file.

        Format: Text segments separated by '--' on its own line.

        Args:
            text_file: Path to text file

        Returns:
            List of text segments
        """
        text_file = Path(text_file)
        if not text_file.exists():
            raise FileNotFoundError(f"Text file not found: {text_file}")

        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split on '--' and filter empty segments
        segments = [s.strip() for s in content.split('--') if s.strip()]

        if not segments:
            raise ValueError(f"No text segments found in {text_file}")

        return segments

    def prepare_text_for_ffmpeg(self, text):
        """
        Prepare text for FFmpeg drawtext filter.

        - Word wrap to max_text_width
        - Escape special characters
        - Preserve intentional line breaks

        Args:
            text: Raw text string

        Returns:
            FFmpeg-escaped text string
        """
        # Word wrap each paragraph
        lines = []
        for paragraph in text.split('\n'):
            if paragraph.strip():
                wrapped = textwrap.fill(
                    paragraph,
                    width=self.max_text_width,
                    break_long_words=False,
                    break_on_hyphens=False
                )
                lines.append(wrapped)
            else:
                lines.append('')

        wrapped_text = '\n'.join(lines)

        # Escape special characters for FFmpeg drawtext
        # Required escapes: \ ' : [ ]
        escaped = wrapped_text.replace('\\', '\\\\')
        escaped = escaped.replace("'", "\\'")
        escaped = escaped.replace(':', '\\:')
        escaped = escaped.replace('[', '\\[')
        escaped = escaped.replace(']', '\\]')

        return escaped

    def add_text_overlay(self, input_video, output_video, text, with_background=False, quality='high'):
        """
        Add text overlay to video using FFmpeg.

        Args:
            input_video: Input video path
            output_video: Output video path
            text: Text to overlay
            with_background: Add semi-transparent background box
            quality: Encoding quality ('high', 'medium', 'fast')
                    high: CRF 18 (near-lossless)
                    medium: CRF 23 (good quality)
                    fast: CRF 28 (smaller files)

        Returns:
            True if successful, False otherwise
        """
        input_video = Path(input_video)
        if not input_video.exists():
            raise FileNotFoundError(f"Input video not found: {input_video}")

        output_video = Path(output_video)
        output_video.parent.mkdir(parents=True, exist_ok=True)

        # Prepare text
        escaped_text = self.prepare_text_for_ffmpeg(text)

        # Build filter
        if with_background:
            vf = self._build_filter_with_background(escaped_text)
        else:
            vf = self._build_filter_simple(escaped_text)

        # Quality settings
        crf_map = {'high': 18, 'medium': 23, 'fast': 28}
        crf = crf_map.get(quality, 18)

        preset_map = {'high': 'slow', 'medium': 'medium', 'fast': 'fast'}
        preset = preset_map.get(quality, 'medium')

        # Build FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', str(input_video),
            '-vf', vf,
            '-c:v', 'libx264',  # H.264 video codec
            '-preset', preset,
            '-crf', str(crf),
            '-c:a', 'copy',  # Copy audio without re-encoding
            '-movflags', '+faststart',  # Web optimization
            '-y',  # Overwrite output
            str(output_video)
        ]

        print(f"Adding text overlay to {input_video.name}...")
        print(f"Font: {self.font_file}")
        print(f"Quality: {quality} (CRF {crf}, preset {preset})")
        if with_background:
            print("Style: Text with background box")
        else:
            print("Style: Text with outline only")

        # Run FFmpeg
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"ERROR: FFmpeg failed")
            print(f"STDERR: {result.stderr}")
            return False

        print(f"SUCCESS: {output_video}")
        return True

    def _build_filter_simple(self, escaped_text):
        """Build simple text overlay filter (fastest)."""
        return (
            f"drawtext="
            f"fontfile='{self.font_file}':"
            f"text='{escaped_text}':"
            f"fontsize={self.font_size}:"
            f"fontcolor=white:"
            f"borderw=3:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2"
        )

    def _build_filter_with_background(self, escaped_text):
        """Build text overlay filter with semi-transparent background box."""
        # First pass: background box
        box_filter = (
            f"drawtext="
            f"fontfile='{self.font_file}':"
            f"text='{escaped_text}':"
            f"fontsize={self.font_size}:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2:"
            f"box=1:"
            f"boxcolor=black@0.7:"
            f"boxborderw=20"
        )

        # Second pass: text on top
        text_filter = (
            f"drawtext="
            f"fontfile='{self.font_file}':"
            f"text='{escaped_text}':"
            f"fontsize={self.font_size}:"
            f"fontcolor=white:"
            f"borderw=2:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2"
        )

        return f"{box_filter},{text_filter}"

    def process_batch(self, input_videos, text_file, output_dir, **kwargs):
        """
        Process multiple videos with text from TextThoughts.txt.

        Each video gets the next text segment in order.

        Args:
            input_videos: List of input video paths
            text_file: Path to TextThoughts.txt
            output_dir: Output directory for processed videos
            **kwargs: Additional arguments for add_text_overlay

        Returns:
            List of (input_path, output_path, success) tuples
        """
        segments = self.read_text_segments(text_file)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = []

        for i, input_video in enumerate(input_videos):
            input_path = Path(input_video)

            # Use modulo to cycle through text segments if more videos than segments
            segment_idx = i % len(segments)
            text = segments[segment_idx]

            output_path = output_dir / f"{input_path.stem}_with_text{input_path.suffix}"

            print(f"\n{'='*60}")
            print(f"Processing {i+1}/{len(input_videos)}: {input_path.name}")
            print(f"Text segment {segment_idx+1}/{len(segments)}")
            print(f"{'='*60}")

            success = self.add_text_overlay(
                input_path,
                output_path,
                text,
                **kwargs
            )

            results.append((input_path, output_path, success))

        return results


def main():
    parser = argparse.ArgumentParser(
        description='Add text overlays to videos using FFmpeg (fastest method)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add text from file (segment 0)
  %(prog)s input.mp4 output.mp4 --text-file TextThoughts.txt --segment 0

  # Add custom text with background
  %(prog)s input.mp4 output.mp4 --text "Your text here" --with-background

  # Process multiple videos with text file
  %(prog)s video1.mp4 video2.mp4 video3.mp4 --text-file TextThoughts.txt --output-dir output/

  # Custom font and size
  %(prog)s input.mp4 output.mp4 --text-file TextThoughts.txt --font /path/to/font.ttf --font-size 60
        """
    )

    parser.add_argument('input', nargs='+', help='Input video file(s)')
    parser.add_argument('output', nargs='?', help='Output video file (required for single input)')

    text_group = parser.add_mutually_exclusive_group(required=True)
    text_group.add_argument('--text', help='Text to overlay')
    text_group.add_argument('--text-file', help='Text file (TextThoughts.txt format)')

    parser.add_argument('--segment', type=int, default=0,
                       help='Text segment index to use (default: 0)')
    parser.add_argument('--output-dir', help='Output directory (for batch processing)')
    parser.add_argument('--with-background', action='store_true',
                       help='Add semi-transparent background box')
    parser.add_argument('--font', help='Path to TTF font file')
    parser.add_argument('--font-size', type=int, default=48,
                       help='Font size in pixels (default: 48)')
    parser.add_argument('--max-width', type=int, default=40,
                       help='Max characters per line (default: 40)')
    parser.add_argument('--quality', choices=['high', 'medium', 'fast'], default='high',
                       help='Encoding quality (default: high)')

    args = parser.parse_args()

    # Validate arguments
    if len(args.input) == 1 and not args.output and not args.output_dir:
        parser.error("Output file or --output-dir required")

    if len(args.input) > 1 and not args.output_dir:
        parser.error("--output-dir required for multiple inputs")

    # Initialize processor
    processor = TextOverlayProcessor(
        font_file=args.font,
        font_size=args.font_size,
        max_text_width=args.max_width
    )

    try:
        # Batch processing
        if args.output_dir:
            if args.text:
                # Use same text for all videos
                for input_video in args.input:
                    input_path = Path(input_video)
                    output_path = Path(args.output_dir) / f"{input_path.stem}_with_text{input_path.suffix}"
                    processor.add_text_overlay(
                        input_video,
                        output_path,
                        args.text,
                        with_background=args.with_background,
                        quality=args.quality
                    )
            else:
                # Use text file - each video gets next segment
                processor.process_batch(
                    args.input,
                    args.text_file,
                    args.output_dir,
                    with_background=args.with_background,
                    quality=args.quality
                )

        # Single file processing
        else:
            if args.text:
                text = args.text
            else:
                segments = processor.read_text_segments(args.text_file)
                if args.segment >= len(segments):
                    print(f"ERROR: Segment {args.segment} not found (only {len(segments)} segments in file)")
                    return 1
                text = segments[args.segment]
                print(f"Using text segment {args.segment + 1}/{len(segments)}")

            success = processor.add_text_overlay(
                args.input[0],
                args.output,
                text,
                with_background=args.with_background,
                quality=args.quality
            )

            return 0 if success else 1

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())

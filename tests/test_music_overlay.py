#!/usr/bin/env python3
"""Quick test of music overlay on a reel"""

from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
from moviepy.audio.fx.AudioFadeIn import AudioFadeIn
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
from pathlib import Path
import sys

if len(sys.argv) < 3:
    print("Usage: python test_music_overlay.py <video.mp4> <music.mp3>")
    sys.exit(1)

video_path = sys.argv[1]
music_path = sys.argv[2]
output_path = "test_with_music.mp4"

print(f"Loading video: {video_path}")
video = VideoFileClip(video_path)
print(f"Video duration: {video.duration:.1f}s")

print(f"Loading music: {music_path}")
music = AudioFileClip(music_path)

# Adjust music to video length
music = music.subclipped(0, min(music.duration, video.duration))
music = music.with_volume_scaled(0.35)
music = AudioFadeIn(2)(music)
music = AudioFadeOut(2)(music)

# Mix with original audio if present
if video.audio:
    print("Mixing music with original video audio...")
    final_audio = CompositeAudioClip([video.audio, music])
else:
    print("No original audio, using music only...")
    final_audio = music

final = video.with_audio(final_audio)

print(f"Writing output: {output_path}")
final.write_videofile(output_path, codec='libx264', audio_codec='aac',
                      audio_bitrate='192k', preset='medium',
                      ffmpeg_params=['-crf', '18'])

print(f"\n✓ Complete! Created: {output_path}")

video.close()
music.close()

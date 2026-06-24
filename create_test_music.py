#!/usr/bin/env python3
"""Create a simple test audio file"""
import numpy as np
from scipy.io import wavfile
import sys

duration = 20  # seconds
sample_rate = 44100

# Generate calm ambient tones (multiple frequencies)
t = np.linspace(0, duration, int(sample_rate * duration))
audio = (
    0.3 * np.sin(2 * np.pi * 220 * t) +  # A3
    0.2 * np.sin(2 * np.pi * 330 * t) +  # E4
    0.15 * np.sin(2 * np.pi * 440 * t)   # A4
) * 0.5  # Overall volume

# Fade in/out
fade_samples = int(sample_rate * 2)
audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)

# Convert to int16
audio = (audio * 32767).astype(np.int16)

output = "music/calm/test_ambient.wav"
wavfile.write(output, sample_rate, audio)
print(f"Created test audio: {output}")

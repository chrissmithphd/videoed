#!/usr/bin/env python3
"""
Programmatic Upbeat Music Generator for Viral Video Background Tracks
Uses SciPy + NumPy for pure Python synthesis (no external dependencies)

Generates 20-second upbeat tracks with drums, bass, and melody at 100 BPM
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import sawtooth, square

# Audio settings
SAMPLE_RATE = 44100  # CD quality
DURATION = 20  # seconds
BPM = 100
BEAT_DURATION = 60 / BPM  # seconds per beat


def generate_time_array(duration_seconds):
    """Generate time array for given duration."""
    return np.linspace(0, duration_seconds, int(SAMPLE_RATE * duration_seconds), False)


def apply_envelope(audio, attack=0.01, decay=0.05, sustain=0.7, release=0.1):
    """Apply ADSR envelope to audio signal."""
    length = len(audio)
    envelope = np.ones(length)

    # Attack
    attack_samples = int(attack * SAMPLE_RATE)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay
    decay_samples = int(decay * SAMPLE_RATE)
    if attack_samples + decay_samples < length:
        envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples)

    # Sustain (already set by initialization)
    sustain_start = attack_samples + decay_samples
    sustain_end = length - int(release * SAMPLE_RATE)
    if sustain_start < sustain_end:
        envelope[sustain_start:sustain_end] = sustain

    # Release
    release_samples = int(release * SAMPLE_RATE)
    if release_samples > 0 and sustain_end < length:
        envelope[sustain_end:] = np.linspace(sustain, 0, length - sustain_end)

    return audio * envelope


def generate_kick_drum(start_time, duration=0.5):
    """Generate kick drum hit (low frequency punch)."""
    t = generate_time_array(duration)

    # Pitch envelope: 150Hz -> 50Hz
    freq = 150 * np.exp(-8 * t / duration) + 50
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE

    # Sine wave with aggressive envelope
    kick = np.sin(phase)
    envelope = np.exp(-6 * t / duration)

    return kick * envelope


def generate_snare(start_time, duration=0.15):
    """Generate snare drum hit (noise + tone)."""
    t = generate_time_array(duration)

    # White noise component
    noise = np.random.uniform(-1, 1, len(t))

    # Tonal component (200Hz)
    tone = np.sin(2 * np.pi * 200 * t)

    # Mix and envelope
    snare = (0.3 * tone + 0.7 * noise)
    envelope = np.exp(-10 * t / duration)

    return snare * envelope


def generate_hihat(start_time, duration=0.08):
    """Generate hi-hat (high frequency noise)."""
    t = generate_time_array(duration)

    # High-pass filtered noise
    noise = np.random.uniform(-1, 1, len(t))

    # Sharp envelope
    envelope = np.exp(-20 * t / duration)

    return noise * envelope * 0.3


def generate_drum_pattern(duration):
    """Generate complete drum pattern (kicks, snares, hi-hats)."""
    samples = int(SAMPLE_RATE * duration)
    drums = np.zeros(samples)

    beat_samples = int(BEAT_DURATION * SAMPLE_RATE)
    num_beats = int(duration / BEAT_DURATION)

    for beat in range(num_beats):
        start_sample = beat * beat_samples

        # Kick on beats 1 and 3 (4/4 time)
        if beat % 4 in [0, 2]:
            kick = generate_kick_drum(beat * BEAT_DURATION)
            kick_samples = min(len(kick), samples - start_sample)
            drums[start_sample:start_sample + kick_samples] += kick[:kick_samples] * 0.8

        # Snare on beats 2 and 4
        if beat % 4 in [1, 3]:
            snare = generate_snare(beat * BEAT_DURATION)
            snare_samples = min(len(snare), samples - start_sample)
            drums[start_sample:start_sample + snare_samples] += snare[:snare_samples] * 0.6

        # Hi-hat on every beat and off-beat
        for subdivision in [0, 0.5]:
            hihat_start = start_sample + int(subdivision * beat_samples)
            if hihat_start < samples:
                hihat = generate_hihat(beat * BEAT_DURATION)
                hihat_samples = min(len(hihat), samples - hihat_start)
                drums[hihat_start:hihat_start + hihat_samples] += hihat[:hihat_samples]

    return drums


def generate_bass_line(duration):
    """Generate bass line using sawtooth wave (energetic, driving)."""
    t = generate_time_array(duration)

    # Bass pattern: root note progression (C2, C2, G1, G1 pattern)
    root_freq = 65.41  # C2
    fifth_freq = 49.0  # G1

    bass = np.zeros(len(t))
    beats_per_bar = 4
    bar_duration = beats_per_bar * BEAT_DURATION

    for bar in range(int(duration / bar_duration)):
        bar_start = int(bar * bar_duration * SAMPLE_RATE)
        bar_samples = int(bar_duration * SAMPLE_RATE)

        # Alternate between root and fifth every bar
        freq = root_freq if bar % 2 == 0 else fifth_freq

        bar_t = t[bar_start:bar_start + bar_samples]
        bar_bass = sawtooth(2 * np.pi * freq * bar_t)

        # Apply envelope to each note
        bar_bass = apply_envelope(bar_bass, attack=0.01, decay=0.1, sustain=0.8, release=0.2)

        bass[bar_start:bar_start + len(bar_bass)] += bar_bass

    return bass * 0.4


def generate_melody(duration):
    """Generate upbeat melody using square wave (bright, energetic)."""
    t = generate_time_array(duration)

    # Melody notes in C major pentatonic (upbeat scale)
    # C4, D4, E4, G4, A4
    notes = [261.63, 293.66, 329.63, 392.00, 440.00]  # Frequencies in Hz

    # Simple repeating pattern (8 notes per bar)
    pattern = [0, 2, 4, 2, 3, 4, 3, 0]  # Index into notes array

    melody = np.zeros(len(t))
    note_duration = BEAT_DURATION / 2  # Eighth notes

    note_index = 0
    for beat in range(int(duration / note_duration)):
        start_sample = int(beat * note_duration * SAMPLE_RATE)
        note_samples = int(note_duration * SAMPLE_RATE)

        freq = notes[pattern[note_index % len(pattern)]]
        note_t = t[start_sample:start_sample + note_samples]

        # Square wave for bright tone
        note = square(2 * np.pi * freq * note_t)

        # Apply envelope
        note = apply_envelope(note, attack=0.005, decay=0.05, sustain=0.6, release=0.15)

        melody[start_sample:start_sample + len(note)] += note
        note_index += 1

    return melody * 0.2


def generate_upbeat_track(duration=20, output_file="upbeat_track.wav"):
    """
    Generate complete upbeat track with drums, bass, and melody.

    Args:
        duration: Track duration in seconds (default: 20)
        output_file: Output WAV file path (default: "upbeat_track.wav")

    Returns:
        Path to generated WAV file
    """
    print(f"Generating {duration}s upbeat track at {BPM} BPM...")

    # Generate individual components
    print("  - Generating drum pattern...")
    drums = generate_drum_pattern(duration)

    print("  - Generating bass line...")
    bass = generate_bass_line(duration)

    print("  - Generating melody...")
    melody = generate_melody(duration)

    # Mix components
    print("  - Mixing tracks...")
    mixed = drums + bass + melody

    # Normalize to prevent clipping
    max_val = np.max(np.abs(mixed))
    if max_val > 0:
        mixed = mixed / max_val * 0.95  # Leave headroom

    # Convert to 16-bit PCM
    audio_data = np.int16(mixed * 32767)

    # Save to WAV file
    wavfile.write(output_file, SAMPLE_RATE, audio_data)
    print(f"✓ Generated: {output_file}")

    return output_file


if __name__ == "__main__":
    import time

    # Benchmark generation speed
    start_time = time.time()
    output_path = generate_upbeat_track(duration=20, output_file="viral_video_music.wav")
    elapsed = time.time() - start_time

    print(f"\nGeneration completed in {elapsed:.2f} seconds")
    print(f"Output: {output_path}")
    print(f"\nTrack specs:")
    print(f"  - Duration: 20 seconds")
    print(f"  - BPM: {BPM}")
    print(f"  - Sample rate: {SAMPLE_RATE} Hz")
    print(f"  - Components: Drums (kick, snare, hi-hat) + Bass + Melody")

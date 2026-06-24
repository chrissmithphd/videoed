#!/usr/bin/env python3
"""
Generate smooth, pleasant background music for viral videos.
Fixes: harsh waveforms, graininess, excessive volume.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, sawtooth
import time

SAMPLE_RATE = 44100
DURATION = 20


def butter_lowpass_filter(data, cutoff, fs, order=5):
    """Apply low-pass filter to remove harsh high frequencies."""
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data)


def generate_time_array(duration_seconds):
    """Generate time array for given duration."""
    return np.linspace(0, duration_seconds, int(SAMPLE_RATE * duration_seconds), False)


def apply_envelope(audio, attack=0.05, decay=0.1, sustain=0.6, release=0.3):
    """Apply smooth ADSR envelope."""
    length = len(audio)
    envelope = np.ones(length)

    attack_samples = int(attack * SAMPLE_RATE)
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples) ** 2  # Curved attack

    decay_samples = int(decay * SAMPLE_RATE)
    if attack_samples + decay_samples < length:
        envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples)

    sustain_start = attack_samples + decay_samples
    sustain_end = length - int(release * SAMPLE_RATE)
    if sustain_start < sustain_end:
        envelope[sustain_start:sustain_end] = sustain

    release_samples = int(release * SAMPLE_RATE)
    if release_samples > 0 and sustain_end < length:
        envelope[sustain_end:] = np.linspace(sustain, 0, length - sustain_end) ** 2  # Curved release

    return audio * envelope


def soft_sine(freq, t, harmonics=2):
    """Generate soft sine wave with subtle harmonics."""
    wave = np.sin(2 * np.pi * freq * t)
    # Add subtle harmonics for warmth
    for i in range(2, harmonics + 1):
        wave += np.sin(2 * np.pi * freq * i * t) / (i ** 2)
    return wave / (1 + sum(1/(i**2) for i in range(2, harmonics + 1)))


def soft_kick(duration_samples, fundamental=60):
    """Generate soft, warm kick drum."""
    t = np.linspace(0, duration_samples / SAMPLE_RATE, duration_samples)

    # Pitch envelope for kick
    freq = fundamental * np.exp(-8 * t)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE

    # Soft sine wave
    kick = np.sin(phase) * np.exp(-5 * t)

    # Low-pass filter for warmth
    kick = butter_lowpass_filter(kick, 150, SAMPLE_RATE, order=4)

    return kick * 0.4  # Reduced volume


def soft_hihat(duration_samples):
    """Generate soft hi-hat."""
    noise = np.random.uniform(-1, 1, duration_samples)
    envelope = np.exp(-30 * np.linspace(0, duration_samples / SAMPLE_RATE, duration_samples))
    hihat = noise * envelope

    # High-pass filtered noise
    hihat = butter_lowpass_filter(hihat, 8000, SAMPLE_RATE, order=3)

    return hihat * 0.15  # Very quiet


def soft_snare(duration_samples):
    """Generate soft snare."""
    t = np.linspace(0, duration_samples / SAMPLE_RATE, duration_samples)

    # Tone component
    tone = np.sin(2 * np.pi * 200 * t) * np.exp(-15 * t)

    # Noise component (body)
    noise = np.random.uniform(-1, 1, duration_samples) * np.exp(-10 * t)
    noise = butter_lowpass_filter(noise, 3000, SAMPLE_RATE, order=3)

    snare = tone * 0.3 + noise * 0.2

    return snare * 0.3  # Reduced volume


# ============================================================================
# STYLE 1: GENTLE ELECTRONIC
# ============================================================================

def generate_gentle_electronic(duration=20):
    """Gentle electronic with soft pads and subtle beats."""
    bpm = 100
    beat_duration = 60 / bpm
    t = generate_time_array(duration)

    # Very subtle drums
    drums = np.zeros(len(t))
    beat_samples = int(beat_duration * SAMPLE_RATE)

    for beat in range(int(duration / beat_duration)):
        start = beat * beat_samples

        # Soft kick every beat
        kick = soft_kick(int(0.4 * SAMPLE_RATE))
        kick_len = min(len(kick), len(drums) - start)
        drums[start:start + kick_len] += kick[:kick_len]

        # Soft hi-hat on off-beats
        if beat % 2 == 1 and start + beat_samples // 2 < len(drums):
            hihat_start = start + beat_samples // 2
            hihat = soft_hihat(int(0.08 * SAMPLE_RATE))
            hihat_len = min(len(hihat), len(drums) - hihat_start)
            drums[hihat_start:hihat_start + hihat_len] += hihat[:hihat_len]

    # Soft pad (C major chord)
    pad = (soft_sine(130.81, t) + soft_sine(164.81, t) + soft_sine(196.00, t)) / 3  # C3, E3, G3
    pad = butter_lowpass_filter(pad, 1200, SAMPLE_RATE, order=3)
    pad *= 0.15  # Very quiet pad

    # Gentle melody
    melody = np.zeros(len(t))
    notes = [261.63, 329.63, 392.00, 523.25]  # C4, E4, G4, C5
    note_dur = beat_duration * 2

    for i in range(int(duration / note_dur)):
        start = int(i * note_dur * SAMPLE_RATE)
        note_samples = int(note_dur * SAMPLE_RATE)
        freq = notes[i % len(notes)]
        note_t = t[start:start + note_samples]
        note = soft_sine(freq, note_t, harmonics=3)
        note = apply_envelope(note, attack=0.1, decay=0.2, sustain=0.5, release=0.3)
        melody[start:start + len(note)] += note * 0.2

    # Mix with reduced levels
    mixed = drums * 0.5 + pad * 0.6 + melody * 0.7

    # Final low-pass to smooth everything
    mixed = butter_lowpass_filter(mixed, 5000, SAMPLE_RATE, order=2)

    # Normalize to -6dB (much quieter than 0dB)
    return mixed / np.max(np.abs(mixed)) * 0.5


# ============================================================================
# STYLE 2: SOFT ACOUSTIC
# ============================================================================

def generate_soft_acoustic(duration=20):
    """Soft acoustic-style with warm tones."""
    bpm = 90
    beat_duration = 60 / bpm
    t = generate_time_array(duration)

    # Very light percussion
    drums = np.zeros(len(t))
    beat_samples = int(beat_duration * SAMPLE_RATE)

    for beat in range(int(duration / beat_duration)):
        start = beat * beat_samples
        if beat % 4 == 0:  # Only on downbeats
            kick = soft_kick(int(0.3 * SAMPLE_RATE), fundamental=80)
            kick_len = min(len(kick), len(drums) - start)
            drums[start:start + kick_len] += kick[:kick_len] * 0.3

    # Warm bass (following chord progression)
    bass = np.zeros(len(t))
    bass_notes = [65.41, 73.42, 98.00, 82.41]  # C2, D2, G2, E2
    bar_dur = beat_duration * 4

    for i in range(int(duration / bar_dur)):
        start = int(i * bar_dur * SAMPLE_RATE)
        bar_samples = int(bar_dur * SAMPLE_RATE)
        freq = bass_notes[i % len(bass_notes)]
        bar_t = t[start:start + bar_samples]

        # Use softened sawtooth
        bass_note = sawtooth(2 * np.pi * freq * bar_t) * 0.5 + soft_sine(freq, bar_t) * 0.5
        bass_note = butter_lowpass_filter(bass_note, 400, SAMPLE_RATE, order=4)
        bass_note = apply_envelope(bass_note, attack=0.05, decay=0.1, sustain=0.7, release=0.2)
        bass[start:start + len(bass_note)] += bass_note * 0.15

    # Gentle arpeggio
    melody = np.zeros(len(t))
    arp_notes = [261.63, 329.63, 392.00, 329.63]  # C4, E4, G4, E4
    note_dur = beat_duration

    for i in range(int(duration / note_dur)):
        start = int(i * note_dur * SAMPLE_RATE)
        note_samples = int(note_dur * SAMPLE_RATE)
        freq = arp_notes[i % len(arp_notes)]
        note_t = t[start:start + note_samples]
        note = soft_sine(freq, note_t, harmonics=4)
        note = apply_envelope(note, attack=0.02, decay=0.1, sustain=0.4, release=0.2)
        melody[start:start + len(note)] += note * 0.2

    # Mix
    mixed = drums * 0.3 + bass * 0.5 + melody * 0.6
    mixed = butter_lowpass_filter(mixed, 6000, SAMPLE_RATE, order=2)

    return mixed / np.max(np.abs(mixed)) * 0.5


# ============================================================================
# STYLE 3: AMBIENT CHILL
# ============================================================================

def generate_ambient_chill(duration=20):
    """Very relaxed ambient background."""
    t = generate_time_array(duration)

    # No drums, just tones

    # Drone bass
    drone = soft_sine(55, t, harmonics=3)  # A1
    drone = butter_lowpass_filter(drone, 300, SAMPLE_RATE, order=4)
    drone *= 0.1

    # Pad layers (A minor chord)
    pad1 = soft_sine(110.00, t, harmonics=2) * 0.08  # A2
    pad2 = soft_sine(130.81, t, harmonics=2) * 0.08  # C3
    pad3 = soft_sine(164.81, t, harmonics=2) * 0.08  # E3

    pad = (pad1 + pad2 + pad3) / 3
    pad = butter_lowpass_filter(pad, 1500, SAMPLE_RATE, order=3)

    # Very slow melody
    melody = np.zeros(len(t))
    notes = [220.00, 261.63, 329.63, 293.66]  # A3, C4, E4, D4
    note_dur = 5.0  # 5 seconds per note

    for i in range(int(duration / note_dur)):
        start = int(i * note_dur * SAMPLE_RATE)
        note_samples = int(note_dur * SAMPLE_RATE)
        freq = notes[i % len(notes)]
        note_t = t[start:start + note_samples]
        note = soft_sine(freq, note_t, harmonics=4)
        note = apply_envelope(note, attack=1.0, decay=0.5, sustain=0.6, release=1.5)
        melody[start:start + len(note)] += note * 0.15

    # Mix
    mixed = drone + pad + melody
    mixed = butter_lowpass_filter(mixed, 4000, SAMPLE_RATE, order=2)

    return mixed / np.max(np.abs(mixed)) * 0.4


def main():
    """Generate 3 smooth, pleasant music styles."""
    print("Generating smooth, pleasant background music...")
    print("=" * 70)

    styles = [
        ("gentle_electronic_100bpm.wav", generate_gentle_electronic, "Gentle Electronic (100 BPM)"),
        ("soft_acoustic_90bpm.wav", generate_soft_acoustic, "Soft Acoustic (90 BPM)"),
        ("ambient_chill.wav", generate_ambient_chill, "Ambient Chill"),
    ]

    start_time = time.time()

    for filename, generator, description in styles:
        print(f"\nGenerating: {description}")

        gen_start = time.time()
        audio = generator(DURATION)
        gen_time = time.time() - gen_start

        # Convert to 16-bit PCM
        audio_int = np.int16(audio * 32767)

        # Save
        wavfile.write(filename, SAMPLE_RATE, audio_int)

        file_size = len(audio_int) * 2 / 1024 / 1024

        print(f"  ✓ Saved: {filename}")
        print(f"  ⏱ Generation time: {gen_time:.2f}s")
        print(f"  📦 File size: {file_size:.1f} MB")

    total_time = time.time() - start_time

    print("\n" + "=" * 70)
    print(f"✓ ALL 3 TRACKS GENERATED in {total_time:.2f} seconds")
    print("=" * 70)
    print("\nImprovements:")
    print("  ✓ Low-pass filtering removes harsh harmonics")
    print("  ✓ Reduced volume (50% of previous)")
    print("  ✓ Soft envelopes with curved attack/release")
    print("  ✓ Warmer waveforms (soft sine, filtered sawtooth)")
    print("  ✓ Better mixing balance")
    print("\nThese tracks should be much more pleasant to listen to!")


if __name__ == "__main__":
    main()

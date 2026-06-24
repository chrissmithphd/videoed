#!/usr/bin/env python3
"""
Test 03 - Create better background music
Generate pleasant, varied music instead of sustained drone
"""
import numpy as np
from scipy.io import wavfile
from pathlib import Path


def create_gentle_melody(duration=20, sample_rate=44100):
    """
    Create a gentle, pleasant melody with variation
    Uses a simple pentatonic scale for a calm, harmonious sound
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Pentatonic scale (C, D, E, G, A) - naturally harmonious
    # frequencies for middle octave
    scale = [261.63, 293.66, 329.63, 392.00, 440.00]  # C4, D4, E4, G4, A4

    # Create a simple melodic pattern
    # Pattern: play each note for 2 seconds with smooth transitions
    note_duration = 2.0  # seconds
    samples_per_note = int(sample_rate * note_duration)
    overlap = int(sample_rate * 0.5)  # 0.5s overlap for smooth transitions

    # Melody pattern (indices into scale)
    melody_pattern = [0, 2, 4, 3, 1, 0, 4, 2, 0, 1]  # Simple pleasant pattern

    for i, note_idx in enumerate(melody_pattern):
        start_sample = i * samples_per_note
        if start_sample >= len(t):
            break

        end_sample = min(start_sample + samples_per_note + overlap, len(t))
        note_t = t[start_sample:end_sample] - t[start_sample]

        # Main frequency
        freq = scale[note_idx]
        note_audio = 0.4 * np.sin(2 * np.pi * freq * note_t)

        # Add subtle harmonics for richness
        note_audio += 0.15 * np.sin(2 * np.pi * freq * 2 * note_t)  # octave
        note_audio += 0.10 * np.sin(2 * np.pi * freq * 1.5 * note_t)  # fifth

        # Envelope: gentle attack and decay
        envelope = np.ones_like(note_t)
        attack_samples = int(sample_rate * 0.3)
        decay_samples = int(sample_rate * 0.4)

        if len(envelope) > attack_samples:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        if len(envelope) > decay_samples:
            envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)

        note_audio *= envelope

        # Mix into full audio
        audio[start_sample:end_sample] += note_audio

    # Normalize
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.6  # Keep some headroom

    # Overall fade in/out
    fade_samples = int(sample_rate * 1.0)
    audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
    audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return audio, sample_rate


def create_ambient_pad(duration=20, sample_rate=44100):
    """
    Create a gentle ambient pad - softer than melody but with movement
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Slowly evolving frequencies (very slow LFO)
    base_freq = 220  # A3
    lfo_freq = 0.1  # Very slow modulation

    # Create evolving pad sound
    for harmonic in [1, 1.5, 2, 3]:
        freq = base_freq * harmonic
        # Add slow frequency modulation
        modulation = 1 + 0.02 * np.sin(2 * np.pi * lfo_freq * t)
        audio += (0.3 / harmonic) * np.sin(2 * np.pi * freq * modulation * t)

    # Add subtle noise for texture
    noise = np.random.normal(0, 0.02, len(t))
    audio += noise

    # Normalize
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.4

    # Fade in/out
    fade_samples = int(sample_rate * 2.0)
    audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
    audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return audio, sample_rate


def create_soft_arpeggio(duration=20, sample_rate=44100):
    """
    Create a soft, gentle arpeggio pattern
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Pentatonic chord: C-E-G (major)
    chord = [261.63, 329.63, 392.00]

    # Arpeggio: play notes in sequence, slowly
    note_duration = 0.8  # Each note plays for 0.8s
    samples_per_note = int(sample_rate * note_duration)

    total_notes = int(duration / note_duration)

    for i in range(total_notes):
        note_idx = i % len(chord)
        freq = chord[note_idx]

        start_sample = i * samples_per_note
        end_sample = min(start_sample + int(samples_per_note * 1.5), len(t))

        if start_sample >= len(t):
            break

        note_t = t[start_sample:end_sample] - t[start_sample]

        # Create note with natural decay
        decay = np.exp(-2 * note_t)
        note_audio = 0.5 * np.sin(2 * np.pi * freq * note_t) * decay

        # Add harmonics
        note_audio += 0.2 * np.sin(2 * np.pi * freq * 2 * note_t) * decay

        audio[start_sample:end_sample] += note_audio[:len(audio[start_sample:end_sample])]

    # Normalize
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.5

    # Fade in/out
    fade_samples = int(sample_rate * 1.5)
    audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
    audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return audio, sample_rate


def main():
    output_dir = Path("../music/calm")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Test 03: Creating better background music options\n")

    # Create three different styles
    styles = [
        ("melody", "Gentle melody with variation", create_gentle_melody),
        ("pad", "Soft ambient pad with movement", create_ambient_pad),
        ("arpeggio", "Soft gentle arpeggio", create_soft_arpeggio),
    ]

    for name, description, func in styles:
        print(f"Creating {name}: {description}")
        audio, sample_rate = func(duration=20)

        # Convert to int16
        audio_int16 = (audio * 32767).astype(np.int16)

        output_path = output_dir / f"bgm_{name}.wav"
        wavfile.write(str(output_path), sample_rate, audio_int16)

        size_kb = output_path.stat().st_size / 1024
        print(f"  ✓ Created: {output_path.name} ({size_kb:.1f} KB)\n")

    print("=" * 60)
    print("CREATED 3 MUSIC OPTIONS:")
    print("  1. bgm_melody.wav - Pleasant melody with variation")
    print("  2. bgm_pad.wav - Soft ambient pad (least intrusive)")
    print("  3. bgm_arpeggio.wav - Gentle arpeggio pattern")
    print("\nAll are 20 seconds, 44.1kHz, pleasant and non-annoying")
    print("=" * 60)

    # Also update the old test file
    print("\nReplacing old annoying test_ambient.wav...")
    audio, sample_rate = create_ambient_pad(duration=20)
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(str(output_dir / "test_ambient.wav"), sample_rate, audio_int16)
    print("✓ Updated test_ambient.wav with better sound")


if __name__ == '__main__':
    main()

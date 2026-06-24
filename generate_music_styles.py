#!/usr/bin/env python3
"""
Generate 5 different upbeat music styles for viral video backgrounds.
Demonstrates variations in BPM, instrumentation, and patterns.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import sawtooth, square
import time


SAMPLE_RATE = 44100
DURATION = 20


def generate_time_array(duration_seconds):
    """Generate time array for given duration."""
    return np.linspace(0, duration_seconds, int(SAMPLE_RATE * duration_seconds), False)


def apply_envelope(audio, attack=0.01, decay=0.05, sustain=0.7, release=0.1):
    """Apply ADSR envelope to audio signal."""
    length = len(audio)
    envelope = np.ones(length)

    attack_samples = int(attack * SAMPLE_RATE)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    decay_samples = int(decay * SAMPLE_RATE)
    if attack_samples + decay_samples < length:
        envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples)

    sustain_start = attack_samples + decay_samples
    sustain_end = length - int(release * SAMPLE_RATE)
    if sustain_start < sustain_end:
        envelope[sustain_start:sustain_end] = sustain

    release_samples = int(release * SAMPLE_RATE)
    if release_samples > 0 and sustain_end < length:
        envelope[sustain_end:] = np.linspace(sustain, 0, length - sustain_end)

    return audio * envelope


# ============================================================================
# STYLE 1: ELECTRONIC DANCE (120 BPM)
# ============================================================================

def generate_electronic_dance(duration=20):
    """Electronic dance style: Fast BPM, 4-on-floor kick, synth stabs."""
    bpm = 120
    beat_duration = 60 / bpm
    t = generate_time_array(duration)

    # 4-on-floor kick pattern
    drums = np.zeros(len(t))
    beat_samples = int(beat_duration * SAMPLE_RATE)

    for beat in range(int(duration / beat_duration)):
        start = beat * beat_samples
        # Kick on every beat
        freq = 150 * np.exp(-8 * np.linspace(0, 0.5, int(0.5 * SAMPLE_RATE)))
        phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
        kick = np.sin(phase) * np.exp(-6 * np.linspace(0, 0.5, len(freq)))
        kick_len = min(len(kick), len(drums) - start)
        drums[start:start + kick_len] += kick[:kick_len] * 0.7

        # Hi-hat on off-beats
        if beat % 2 == 1:
            hihat_start = start + beat_samples // 2
            if hihat_start < len(drums):
                noise = np.random.uniform(-1, 1, int(0.05 * SAMPLE_RATE))
                noise *= np.exp(-20 * np.linspace(0, 0.05, len(noise)))
                hihat_len = min(len(noise), len(drums) - hihat_start)
                drums[hihat_start:hihat_start + hihat_len] += noise[:hihat_len] * 0.3

    # Synth bass (sawtooth)
    bass = sawtooth(2 * np.pi * 55 * t) * 0.3  # A1

    # Synth stabs (square wave arpeggios)
    melody = np.zeros(len(t))
    notes = [220, 277.18, 329.63, 440]  # A3, C#4, E4, A4 (A major chord)
    note_dur = beat_duration / 4

    for i in range(int(duration / note_dur)):
        start = int(i * note_dur * SAMPLE_RATE)
        note_samples = int(note_dur * SAMPLE_RATE)
        freq = notes[i % len(notes)]
        note_t = t[start:start + note_samples]
        note = square(2 * np.pi * freq * note_t)
        note = apply_envelope(note, attack=0.001, decay=0.05, sustain=0.3, release=0.1)
        melody[start:start + len(note)] += note * 0.15

    # Mix
    mixed = drums + bass + melody
    return mixed / np.max(np.abs(mixed)) * 0.95


# ============================================================================
# STYLE 2: FUNK GROOVE (90 BPM)
# ============================================================================

def generate_funk_groove(duration=20):
    """Funk style: Syncopated drums, funky bass line, clean rhythm."""
    bpm = 90
    beat_duration = 60 / bpm
    t = generate_time_array(duration)

    # Syncopated drum pattern
    drums = np.zeros(len(t))
    beat_samples = int(beat_duration * SAMPLE_RATE)

    for beat in range(int(duration / beat_duration)):
        start = beat * beat_samples

        # Kick on 1 and 3.5 (syncopation)
        if beat % 4 in [0, 3]:
            freq = 120 * np.exp(-6 * np.linspace(0, 0.4, int(0.4 * SAMPLE_RATE)))
            phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
            kick = np.sin(phase) * np.exp(-5 * np.linspace(0, 0.4, len(freq)))
            offset = beat_samples // 2 if beat % 4 == 3 else 0
            kick_start = start + offset
            kick_len = min(len(kick), len(drums) - kick_start)
            drums[kick_start:kick_start + kick_len] += kick[:kick_len] * 0.6

        # Snare on 2 and 4
        if beat % 4 in [1, 3]:
            noise = np.random.uniform(-1, 1, int(0.12 * SAMPLE_RATE))
            tone = np.sin(2 * np.pi * 180 * np.linspace(0, 0.12, len(noise)))
            snare = (0.3 * tone + 0.7 * noise) * np.exp(-8 * np.linspace(0, 0.12, len(noise)))
            snare_len = min(len(snare), len(drums) - start)
            drums[start:start + snare_len] += snare[:snare_len] * 0.5

    # Funky bass (octave jumps)
    bass = np.zeros(len(t))
    for bar in range(int(duration / (4 * beat_duration))):
        bar_start = int(bar * 4 * beat_duration * SAMPLE_RATE)
        bar_samples = int(4 * beat_duration * SAMPLE_RATE)
        # Alternating octaves: E1, E2, E1, E2
        freqs = [41.20, 82.41, 41.20, 82.41]  # E1, E2
        for i, freq in enumerate(freqs):
            note_start = bar_start + i * bar_samples // 4
            note_samples = bar_samples // 4
            note_t = t[note_start:note_start + note_samples]
            note = sawtooth(2 * np.pi * freq * note_t)
            note = apply_envelope(note, attack=0.005, decay=0.1, sustain=0.6, release=0.15)
            bass[note_start:note_start + len(note)] += note * 0.35

    # Clean guitar-like melody (sine waves)
    melody = np.zeros(len(t))
    notes = [164.81, 196.00, 220.00, 246.94]  # E3, G3, A3, B3 (E minor pentatonic)
    note_dur = beat_duration

    for i in range(int(duration / note_dur)):
        start = int(i * note_dur * SAMPLE_RATE)
        note_samples = int(note_dur * SAMPLE_RATE)
        freq = notes[i % len(notes)]
        note_t = t[start:start + note_samples]
        note = np.sin(2 * np.pi * freq * note_t)
        note = apply_envelope(note, attack=0.01, decay=0.1, sustain=0.7, release=0.2)
        melody[start:start + len(note)] += note * 0.2

    # Mix
    mixed = drums + bass + melody
    return mixed / np.max(np.abs(mixed)) * 0.95


# ============================================================================
# STYLE 3: UPBEAT ROCK (110 BPM)
# ============================================================================

def generate_upbeat_rock(duration=20):
    """Rock style: Driving drums, power chord bass, energetic rhythm."""
    bpm = 110
    beat_duration = 60 / bpm
    t = generate_time_array(duration)

    # Rock drum pattern (heavy on kick and snare)
    drums = np.zeros(len(t))
    beat_samples = int(beat_duration * SAMPLE_RATE)

    for beat in range(int(duration / beat_duration)):
        start = beat * beat_samples

        # Heavy kick on 1 and 3
        if beat % 4 in [0, 2]:
            freq = 140 * np.exp(-7 * np.linspace(0, 0.45, int(0.45 * SAMPLE_RATE)))
            phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
            kick = np.sin(phase) * np.exp(-5 * np.linspace(0, 0.45, len(freq)))
            kick_len = min(len(kick), len(drums) - start)
            drums[start:start + kick_len] += kick[:kick_len] * 0.8

        # Loud snare on 2 and 4
        if beat % 4 in [1, 3]:
            noise = np.random.uniform(-1, 1, int(0.15 * SAMPLE_RATE))
            tone = np.sin(2 * np.pi * 200 * np.linspace(0, 0.15, len(noise)))
            snare = (0.4 * tone + 0.6 * noise) * np.exp(-9 * np.linspace(0, 0.15, len(noise)))
            snare_len = min(len(snare), len(drums) - start)
            drums[start:start + snare_len] += snare[:snare_len] * 0.65

        # Continuous hi-hat
        hihat = np.random.uniform(-1, 1, int(0.08 * SAMPLE_RATE))
        hihat *= np.exp(-18 * np.linspace(0, 0.08, len(hihat)))
        hihat_len = min(len(hihat), len(drums) - start)
        drums[start:start + hihat_len] += hihat[:hihat_len] * 0.25

    # Power chord bass (distorted sawtooth)
    bass = np.zeros(len(t))
    root_freq = 73.42  # D2
    fifth_freq = 110.00  # A2

    for bar in range(int(duration / (4 * beat_duration))):
        bar_start = int(bar * 4 * beat_duration * SAMPLE_RATE)
        half_bar = int(2 * beat_duration * SAMPLE_RATE)

        # Root for first half
        bass_t = t[bar_start:bar_start + half_bar]
        bass[bar_start:bar_start + half_bar] += sawtooth(2 * np.pi * root_freq * bass_t) * 0.4

        # Fifth for second half
        fifth_start = bar_start + half_bar
        bass_t = t[fifth_start:fifth_start + half_bar]
        if fifth_start + half_bar < len(bass):
            bass[fifth_start:fifth_start + half_bar] += sawtooth(2 * np.pi * fifth_freq * bass_t) * 0.4

    # Distortion (clip)
    bass = np.clip(bass, -0.5, 0.5)

    # Melody (octave jumps, square wave)
    melody = np.zeros(len(t))
    notes = [293.66, 329.63, 392.00, 293.66]  # D4, E4, G4, D4
    note_dur = beat_duration / 2

    for i in range(int(duration / note_dur)):
        start = int(i * note_dur * SAMPLE_RATE)
        note_samples = int(note_dur * SAMPLE_RATE)
        freq = notes[i % len(notes)]
        note_t = t[start:start + note_samples]
        note = square(2 * np.pi * freq * note_t)
        note = apply_envelope(note, attack=0.005, decay=0.05, sustain=0.65, release=0.12)
        melody[start:start + len(note)] += note * 0.18

    # Mix
    mixed = drums + bass + melody
    return mixed / np.max(np.abs(mixed)) * 0.95


# ============================================================================
# STYLE 4: TROPICAL HOUSE (100 BPM)
# ============================================================================

def generate_tropical_house(duration=20):
    """Tropical house style: Relaxed drums, marimba-like melody, airy feel."""
    bpm = 100
    beat_duration = 60 / bpm
    t = generate_time_array(duration)

    # Relaxed kick pattern
    drums = np.zeros(len(t))
    beat_samples = int(beat_duration * SAMPLE_RATE)

    for beat in range(int(duration / beat_duration)):
        start = beat * beat_samples

        # Soft kick on every other beat
        if beat % 2 == 0:
            freq = 130 * np.exp(-6 * np.linspace(0, 0.5, int(0.5 * SAMPLE_RATE)))
            phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
            kick = np.sin(phase) * np.exp(-5 * np.linspace(0, 0.5, len(freq)))
            kick_len = min(len(kick), len(drums) - start)
            drums[start:start + kick_len] += kick[:kick_len] * 0.5

        # Light clap on 2 and 4
        if beat % 4 in [1, 3]:
            noise = np.random.uniform(-1, 1, int(0.08 * SAMPLE_RATE))
            clap = noise * np.exp(-12 * np.linspace(0, 0.08, len(noise)))
            clap_len = min(len(clap), len(drums) - start)
            drums[start:start + clap_len] += clap[:clap_len] * 0.35

    # Bass (sub bass, very low sine)
    bass = np.sin(2 * np.pi * 50 * t) * 0.25  # G1 sub bass

    # Marimba-like melody (sine with quick decay)
    melody = np.zeros(len(t))
    notes = [523.25, 587.33, 659.25, 783.99, 880.00]  # C5, D5, E5, G5, A5 (pentatonic)
    note_dur = beat_duration / 2

    for i in range(int(duration / note_dur)):
        start = int(i * note_dur * SAMPLE_RATE)
        note_samples = int(note_dur * SAMPLE_RATE)
        freq = notes[i % len(notes)]
        note_t = t[start:start + note_samples]
        # Marimba-like: sine with harmonics
        note = np.sin(2 * np.pi * freq * note_t) * 0.6
        note += np.sin(2 * np.pi * freq * 2 * note_t) * 0.3  # 2nd harmonic
        note += np.sin(2 * np.pi * freq * 3 * note_t) * 0.1  # 3rd harmonic
        note = apply_envelope(note, attack=0.001, decay=0.15, sustain=0.2, release=0.2)
        melody[start:start + len(note)] += note * 0.15

    # Mix
    mixed = drums + bass + melody
    return mixed / np.max(np.abs(mixed)) * 0.95


# ============================================================================
# STYLE 5: HIP-HOP TRAP (85 BPM)
# ============================================================================

def generate_hiphop_trap(duration=20):
    """Hip-hop trap style: 808 bass, snare rolls, hi-hat triplets."""
    bpm = 85
    beat_duration = 60 / bpm
    t = generate_time_array(duration)

    # Trap drums (heavy 808 kick + snare rolls)
    drums = np.zeros(len(t))
    beat_samples = int(beat_duration * SAMPLE_RATE)

    for beat in range(int(duration / beat_duration)):
        start = beat * beat_samples

        # 808 kick (long sustain)
        if beat % 4 in [0, 2]:
            freq = 160 * np.exp(-5 * np.linspace(0, 0.8, int(0.8 * SAMPLE_RATE)))
            phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
            kick = np.sin(phase) * np.exp(-3 * np.linspace(0, 0.8, len(freq)))
            kick_len = min(len(kick), len(drums) - start)
            drums[start:start + kick_len] += kick[:kick_len] * 0.75

        # Snare on 2 and 4
        if beat % 4 in [1, 3]:
            noise = np.random.uniform(-1, 1, int(0.12 * SAMPLE_RATE))
            tone = np.sin(2 * np.pi * 220 * np.linspace(0, 0.12, len(noise)))
            snare = (0.2 * tone + 0.8 * noise) * np.exp(-10 * np.linspace(0, 0.12, len(noise)))
            snare_len = min(len(snare), len(drums) - start)
            drums[start:start + snare_len] += snare[:snare_len] * 0.55

        # Hi-hat triplets (rapid)
        for triplet in range(3):
            hihat_start = start + (triplet * beat_samples // 3)
            if hihat_start < len(drums):
                noise = np.random.uniform(-1, 1, int(0.04 * SAMPLE_RATE))
                hihat = noise * np.exp(-25 * np.linspace(0, 0.04, len(noise)))
                hihat_len = min(len(hihat), len(drums) - hihat_start)
                drums[hihat_start:hihat_start + hihat_len] += hihat[:hihat_len] * 0.28

    # Sub bass (sine wave, very low)
    bass = np.zeros(len(t))
    for bar in range(int(duration / (4 * beat_duration))):
        bar_start = int(bar * 4 * beat_duration * SAMPLE_RATE)
        bar_samples = int(4 * beat_duration * SAMPLE_RATE)
        # Simple root note
        bass_t = t[bar_start:bar_start + bar_samples]
        bass[bar_start:bar_start + bar_samples] += np.sin(2 * np.pi * 55 * bass_t) * 0.4  # A1

    # Melody (bell-like square wave)
    melody = np.zeros(len(t))
    notes = [440, 493.88, 523.25, 659.25]  # A4, B4, C5, E5
    note_dur = beat_duration

    for i in range(int(duration / note_dur)):
        start = int(i * note_dur * SAMPLE_RATE)
        note_samples = int(note_dur * SAMPLE_RATE)
        freq = notes[i % len(notes)]
        note_t = t[start:start + note_samples]
        note = square(2 * np.pi * freq * note_t)
        note = apply_envelope(note, attack=0.005, decay=0.08, sustain=0.4, release=0.15)
        melody[start:start + len(note)] += note * 0.12

    # Mix
    mixed = drums + bass + melody
    return mixed / np.max(np.abs(mixed)) * 0.95


# ============================================================================
# MAIN: GENERATE ALL 5 STYLES
# ============================================================================

def main():
    """Generate all 5 music styles."""
    styles = [
        ("electronic_dance_120bpm.wav", generate_electronic_dance, "Electronic Dance (120 BPM)"),
        ("funk_groove_90bpm.wav", generate_funk_groove, "Funk Groove (90 BPM)"),
        ("upbeat_rock_110bpm.wav", generate_upbeat_rock, "Upbeat Rock (110 BPM)"),
        ("tropical_house_100bpm.wav", generate_tropical_house, "Tropical House (100 BPM)"),
        ("hiphop_trap_85bpm.wav", generate_hiphop_trap, "Hip-Hop Trap (85 BPM)"),
    ]

    print("=" * 70)
    print("GENERATING 5 UPBEAT MUSIC STYLES FOR VIRAL VIDEO BACKGROUNDS")
    print("=" * 70)
    print()

    total_start = time.time()

    for filename, generator_func, description in styles:
        print(f"Generating: {description}")
        start = time.time()

        audio = generator_func(duration=DURATION)
        audio_data = np.int16(audio * 32767)
        wavfile.write(filename, SAMPLE_RATE, audio_data)

        elapsed = time.time() - start
        file_size = len(audio_data) * 2 / (1024 * 1024)  # Size in MB

        print(f"  ✓ Saved: {filename}")
        print(f"  ⏱ Generation time: {elapsed:.2f}s")
        print(f"  📦 File size: {file_size:.1f} MB")
        print()

    total_elapsed = time.time() - total_start
    print("=" * 70)
    print(f"✓ ALL 5 TRACKS GENERATED in {total_elapsed:.2f} seconds")
    print("=" * 70)
    print()
    print("SUMMARY:")
    print("  1. electronic_dance_120bpm.wav - Fast 4-on-floor beats, synth stabs")
    print("  2. funk_groove_90bpm.wav - Syncopated drums, funky octave bass")
    print("  3. upbeat_rock_110bpm.wav - Driving drums, power chord bass")
    print("  4. tropical_house_100bpm.wav - Relaxed marimba melody, sub bass")
    print("  5. hiphop_trap_85bpm.wav - 808 bass, snare rolls, hi-hat triplets")
    print()
    print("Use these tracks as viral video backgrounds!")


if __name__ == "__main__":
    main()

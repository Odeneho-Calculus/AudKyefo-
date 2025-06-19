#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate sample audio files for testing
"""

import os
import sys
import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine

def generate_sine_wave(duration_ms=5000, freq=440, sample_rate=44100):
    """
    Generate a sine wave audio segment

    Args:
        duration_ms: Duration in milliseconds
        freq: Frequency in Hz
        sample_rate: Sample rate in Hz

    Returns:
        AudioSegment containing the sine wave
    """
    sine_generator = Sine(freq, sample_rate=sample_rate)
    return sine_generator.to_audio_segment(duration=duration_ms)

def generate_sample_files():
    """Generate sample audio files for testing"""
    # Create the sample_audio directory if it doesn't exist
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_audio")
    if not os.path.exists(sample_dir):
        os.makedirs(sample_dir)

    # Generate a 5-second sine wave
    print("Generating 5-second sine wave...")
    sine_wave = generate_sine_wave(5000, 440)

    # Export in different formats
    formats = [
        ("mp3", "mp3"),
        ("wav", "wav"),
        ("ogg", "ogg"),
        ("flac", "flac"),
        ("m4a", "mp4")
    ]

    for name, fmt in formats:
        output_path = os.path.join(sample_dir, f"sine_440hz_5s.{name}")
        print(f"Exporting {output_path}...")
        sine_wave.export(output_path, format=fmt)

    # Generate a longer sample with multiple frequencies
    print("Generating 30-second multi-frequency sample...")
    segments = []

    # 10 seconds of 440 Hz
    segments.append(generate_sine_wave(10000, 440))

    # 10 seconds of 880 Hz
    segments.append(generate_sine_wave(10000, 880))

    # 10 seconds of 220 Hz
    segments.append(generate_sine_wave(10000, 220))

    # Combine the segments
    multi_freq = segments[0] + segments[1] + segments[2]

    # Export in MP3 format
    output_path = os.path.join(sample_dir, "multi_freq_30s.mp3")
    print(f"Exporting {output_path}...")
    multi_freq.export(output_path, format="mp3")

    print("Sample audio files generated successfully.")

if __name__ == "__main__":
    generate_sample_files()
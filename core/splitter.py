"""
Audio splitting algorithms for AudKyɛfo
"""

import os
import logging
from typing import List, Tuple, Callable, Optional
from pydub import AudioSegment

from utils.constants import (
    SPLIT_METHOD_EQUAL,
    SPLIT_METHOD_DURATION,
    SPLIT_METHOD_CUSTOM,
    PROGRESS_SPLITTING_START,
    PROGRESS_SPLITTING_END
)
from utils.helpers import generate_output_filename

# Set up logging
logger = logging.getLogger(__name__)

def split_audio(
    audio: AudioSegment,
    method: str,
    output_dir: str,
    original_name: str,
    output_format: str,
    naming_pattern: str,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    **kwargs
) -> List[str]:
    """
    Split audio using the specified method

    Args:
        audio: AudioSegment to split
        method: Splitting method (equal_parts, fixed_duration, custom_ranges)
        output_dir: Output directory
        original_name: Original file name without extension
        output_format: Output format
        naming_pattern: Naming pattern for output files
        progress_callback: Function for progress updates
        **kwargs: Additional parameters for the splitting method
            - num_parts: Number of equal parts (for equal_parts method)
            - duration: Duration in seconds (for fixed_duration method)
            - ranges: List of (start, end) tuples in seconds (for custom_ranges method)
            - overlap: Overlap duration in seconds

    Returns:
        List of paths to the created audio files
    """
    if method == SPLIT_METHOD_EQUAL:
        return split_equal_parts(
            audio, output_dir, original_name, output_format, naming_pattern,
            progress_callback, **kwargs
        )
    elif method == SPLIT_METHOD_DURATION:
        return split_fixed_duration(
            audio, output_dir, original_name, output_format, naming_pattern,
            progress_callback, **kwargs
        )
    elif method == SPLIT_METHOD_CUSTOM:
        return split_custom_ranges(
            audio, output_dir, original_name, output_format, naming_pattern,
            progress_callback, **kwargs
        )
    else:
        raise ValueError(f"Unknown splitting method: {method}")

def split_equal_parts(
    audio: AudioSegment,
    output_dir: str,
    original_name: str,
    output_format: str,
    naming_pattern: str,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    **kwargs
) -> List[str]:
    """
    Split audio into equal parts

    Args:
        audio: AudioSegment to split
        output_dir: Output directory
        original_name: Original file name without extension
        output_format: Output format
        naming_pattern: Naming pattern for output files
        progress_callback: Function for progress updates
        **kwargs: Additional parameters
            - num_parts: Number of equal parts
            - overlap: Overlap duration in seconds

    Returns:
        List of paths to the created audio files
    """
    num_parts = kwargs.get("num_parts", 2)
    overlap = kwargs.get("overlap", 0)

    if num_parts < 2:
        raise ValueError("Number of parts must be at least 2")

    total_duration = len(audio)
    part_duration = total_duration / num_parts

    if part_duration <= 0:
        raise ValueError("Part duration is too small")

    output_files = []

    for i in range(num_parts):
        # Calculate progress
        progress = PROGRESS_SPLITTING_START + (PROGRESS_SPLITTING_END - PROGRESS_SPLITTING_START) * (i / num_parts)
        if progress_callback:
            progress_callback(int(progress), f"Creating part {i+1} of {num_parts}...")

        # Calculate start and end times
        start_time = max(0, i * part_duration - overlap)
        end_time = min(total_duration, (i + 1) * part_duration + overlap)

        # Extract segment
        segment = audio[start_time:end_time]

        # Generate output filename
        filename = generate_output_filename(
            original_name, i+1,
            start_time/1000, end_time/1000,  # Convert to seconds
            pattern=naming_pattern,
            extension=output_format
        )
        output_path = os.path.join(output_dir, filename)

        # Export segment
        segment.export(output_path, format=output_format)
        output_files.append(output_path)

    return output_files

def split_fixed_duration(
    audio: AudioSegment,
    output_dir: str,
    original_name: str,
    output_format: str,
    naming_pattern: str,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    **kwargs
) -> List[str]:
    """
    Split audio into segments of fixed duration

    Args:
        audio: AudioSegment to split
        output_dir: Output directory
        original_name: Original file name without extension
        output_format: Output format
        naming_pattern: Naming pattern for output files
        progress_callback: Function for progress updates
        **kwargs: Additional parameters
            - duration: Duration in seconds
            - overlap: Overlap duration in seconds

    Returns:
        List of paths to the created audio files
    """
    duration = kwargs.get("duration", 60)  # Default to 60 seconds
    overlap = kwargs.get("overlap", 0)

    if duration <= 0:
        raise ValueError("Duration must be greater than 0")

    total_duration = len(audio)
    duration_ms = duration * 1000  # Convert to milliseconds
    overlap_ms = overlap * 1000  # Convert to milliseconds

    # Calculate number of parts
    num_parts = max(1, int((total_duration + overlap_ms) / (duration_ms - overlap_ms)))

    output_files = []

    for i in range(num_parts):
        # Calculate progress
        progress = PROGRESS_SPLITTING_START + (PROGRESS_SPLITTING_END - PROGRESS_SPLITTING_START) * (i / num_parts)
        if progress_callback:
            progress_callback(int(progress), f"Creating part {i+1} of {num_parts}...")

        # Calculate start and end times
        start_time = max(0, i * (duration_ms - overlap_ms))
        end_time = min(total_duration, start_time + duration_ms)

        # Break if we've reached the end
        if start_time >= total_duration:
            break

        # Extract segment
        segment = audio[start_time:end_time]

        # Generate output filename
        filename = generate_output_filename(
            original_name, i+1,
            start_time/1000, end_time/1000,  # Convert to seconds
            pattern=naming_pattern,
            extension=output_format
        )
        output_path = os.path.join(output_dir, filename)

        # Export segment
        segment.export(output_path, format=output_format)
        output_files.append(output_path)

    return output_files

def split_custom_ranges(
    audio: AudioSegment,
    output_dir: str,
    original_name: str,
    output_format: str,
    naming_pattern: str,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    **kwargs
) -> List[str]:
    """
    Split audio based on custom time ranges

    Args:
        audio: AudioSegment to split
        output_dir: Output directory
        original_name: Original file name without extension
        output_format: Output format
        naming_pattern: Naming pattern for output files
        progress_callback: Function for progress updates
        **kwargs: Additional parameters
            - ranges: List of (start, end) tuples in seconds

    Returns:
        List of paths to the created audio files
    """
    ranges = kwargs.get("ranges", [])

    if not ranges:
        raise ValueError("No time ranges specified")

    total_duration = len(audio)
    output_files = []

    for i, (start_sec, end_sec) in enumerate(ranges):
        # Calculate progress
        progress = PROGRESS_SPLITTING_START + (PROGRESS_SPLITTING_END - PROGRESS_SPLITTING_START) * (i / len(ranges))
        if progress_callback:
            progress_callback(int(progress), f"Creating segment {i+1} of {len(ranges)}...")

        # Convert to milliseconds
        start_time = max(0, start_sec * 1000)
        end_time = min(total_duration, end_sec * 1000)

        # Skip invalid ranges
        if start_time >= end_time or start_time >= total_duration:
            logger.warning(f"Skipping invalid range: {start_sec}-{end_sec}")
            continue

        # Extract segment
        segment = audio[start_time:end_time]

        # Generate output filename
        filename = generate_output_filename(
            original_name, i+1,
            start_sec, end_sec,
            pattern=naming_pattern,
            extension=output_format
        )
        output_path = os.path.join(output_dir, filename)

        # Export segment
        segment.export(output_path, format=output_format)
        output_files.append(output_path)

    return output_files
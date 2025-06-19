#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run script for AudKyɛfo
This script checks for required packages and installs them if needed before running the application.
"""

import sys
import subprocess
import importlib.util
import os
import platform

# Required packages
REQUIRED_PACKAGES = [
    "PyQt5",
    "pydub",
    "mutagen",
    "numpy",
    "PyQt5.QtMultimedia"
]

def check_package(package_name):
    """Check if a package is installed"""
    return importlib.util.find_spec(package_name) is not None

def install_package(package_name):
    """Install a package using pip"""
    print(f"Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}. Please install it manually.")
        return False

def check_and_install_packages():
    """Check for required packages and install them if needed"""
    all_packages_installed = True

    for package in REQUIRED_PACKAGES:
        if not check_package(package):
            print(f"{package} is not installed.")
            if not install_package(package):
                all_packages_installed = False
        else:
            print(f"{package} is already installed.")

    return all_packages_installed

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print("FFmpeg is installed.")
            return True
        else:
            print("FFmpeg is not installed or not in PATH.")
            return False
    except FileNotFoundError:
        print("FFmpeg is not installed or not in PATH.")
        return False

def install_ffmpeg():
    """Provide instructions for installing FFmpeg"""
    system = platform.system()

    print("\nFFmpeg is required for audio processing.")
    print("Please install FFmpeg using the following instructions:")

    if system == "Windows":
        print("\nWindows:")
        print("1. Download FFmpeg from https://ffmpeg.org/download.html")
        print("2. Extract the files to a folder (e.g., C:\\ffmpeg)")
        print("3. Add the bin folder to your PATH environment variable")
        print("   (e.g., C:\\ffmpeg\\bin)")

    elif system == "Darwin":  # macOS
        print("\nmacOS:")
        print("1. Install Homebrew if you don't have it: https://brew.sh/")
        print("2. Run: brew install ffmpeg")

    else:  # Linux
        print("\nLinux:")
        print("Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("Fedora: sudo dnf install ffmpeg")
        print("Arch Linux: sudo pacman -S ffmpeg")

    print("\nAfter installing FFmpeg, restart the application.")
    return False

def main_wrapper():
    """Check dependencies and run the main application"""
    print("Checking dependencies...")

    # Check Python packages
    if not check_and_install_packages():
        print("\nSome required packages could not be installed.")
        print("Please install them manually and try again.")
        return 1

    # Check FFmpeg
    if not check_ffmpeg():
        install_ffmpeg()
        return 1

    # All dependencies are installed, run the main application
    print("\nAll dependencies are installed. Starting AudKyɛfo...\n")

    # Import main after ensuring all dependencies are installed
    from main import main
    return main()

if __name__ == "__main__":
    sys.exit(main_wrapper())
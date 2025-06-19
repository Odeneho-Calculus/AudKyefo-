#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build script for creating a standalone executable of AudKyɛfo
"""

import os
import sys
import shutil
import subprocess
import platform

def main():
    """Main function to build the executable"""
    print("Building AudKyɛfo executable...")

    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Create the build directory if it doesn't exist
    build_dir = os.path.join(current_dir, "build")
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    # Create the dist directory if it doesn't exist
    dist_dir = os.path.join(current_dir, "dist")
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)

    # Determine the icon path
    icon_path = os.path.join(current_dir, "resources", "icons", "app.png")
    if not os.path.exists(icon_path):
        print("Warning: Icon file not found at", icon_path)
        icon_path = None

    # Build the PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=AudKyefo",
        "--add-data=resources;resources",
    ]

    # Add icon if available
    if icon_path:
        cmd.append(f"--icon={icon_path}")

    # Add the main script
    cmd.append(os.path.join(current_dir, "main.py"))

    # Run PyInstaller
    print("Running PyInstaller with command:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
        print("PyInstaller completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error running PyInstaller: {e}")
        return 1
    except FileNotFoundError:
        print("Error: PyInstaller not found. Please install it with 'pip install pyinstaller'")
        return 1

    # Copy ffmpeg binaries if needed
    if platform.system() == "Windows":
        try:
            # Check if ffmpeg is installed
            ffmpeg_path = shutil.which("ffmpeg")
            if ffmpeg_path:
                # Copy ffmpeg.exe to the dist directory
                shutil.copy(ffmpeg_path, os.path.join(dist_dir, "ffmpeg.exe"))
                print(f"Copied ffmpeg from {ffmpeg_path} to dist directory")
            else:
                print("Warning: ffmpeg not found in PATH. The application may not work correctly.")
        except Exception as e:
            print(f"Error copying ffmpeg: {e}")

    print("Build completed successfully")
    print(f"Executable can be found at: {os.path.join(dist_dir, 'AudKyefo.exe')}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
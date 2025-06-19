"""
AudKyɛfo - Audio Splitter
Main package initialization
"""

# Add the package to the Python path when imported
import os
import sys

# Get the package root directory
package_root = os.path.dirname(os.path.abspath(__file__))

# Add the package root to the Python path if it's not already there
if package_root not in sys.path:
    sys.path.insert(0, package_root)
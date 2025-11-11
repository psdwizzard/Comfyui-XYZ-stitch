"""
XYZ Grid Custom Nodes for ComfyUI
A1111-style XYZ plot functionality for parameter exploration
"""

from .xyz_grid_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print("XYZ Grid nodes loaded successfully!")
print("")
print("EASY MODE (Recommended):")
print("- XYZ Grid Input: Generate combinations one at a time")
print("- XYZ String to Number: Convert string values to INT/FLOAT")
print("- XYZ Auto Collector: Automatically collects and outputs")
print("- XYZ Grid Stitch: Create the final comparison grid")
print("  * NEW: A1111 Style layout option! (X blocks with Y×Z grids inside)")
print("")
print("See EASY_GUIDE.md for the simplest workflow!")
print("See A1111_STYLE_GUIDE.md for the classic A1111 layout!")
print("")
print("Advanced nodes: Image Collector (Manual), Grid Input (Batch), Grid Iterator")

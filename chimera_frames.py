#!/usr/bin/env python
# ChimeraX script for batch processing RNA PDB files and generating screenshots
# Run with: chimerax --offscreen --script chimera_frames.py
#


import os
import glob
import sys
import re

# ===== CONFIGURATION - CHANGE THIS PATH =====
folder_path = '/your/path/to/pdbs'  # Your PDB folder path
# ============================================

def natural_sort_key(filename):
    """Natural sort: split text and numeric parts so 2 < 10."""
    basename = os.path.basename(filename)
    parts = []
    for part in re.split(r'(\d+)', basename):
        parts.append(int(part) if part.isdigit() else part.lower())
    return parts

# Collect PDBs, sorted naturally
pdb_files = glob.glob(os.path.join(folder_path, '*.pdb'))
pdb_files = sorted(pdb_files, key=natural_sort_key)

if not pdb_files:
    print(f"No PDB files found in {folder_path}")
    sys.exit(1)

# Output dir
output_folder = os.path.join(folder_path, 'screenshots')
os.makedirs(output_folder, exist_ok=True)

print(f"Found {len(pdb_files)} PDB files in {folder_path}")
print(f"Screenshots will be saved to {output_folder}")
print("\nProcessing order:")
for i, pdb_file in enumerate(pdb_files[:10]):
    print(f"  {i+1}. {os.path.basename(pdb_file)}")
if len(pdb_files) > 10:
    print(f"  ... and {len(pdb_files) - 10} more files")
print()

# Ensure we're running inside ChimeraX
if 'session' not in globals():
    print("Error: This script must be run from within ChimeraX")
    print("Use: chimerax --nogui --script chimera_frames_byelement.py")
    sys.exit(1)

# ChimeraX command runner
from chimerax.core.commands import run as cmd

successful_saves = 0

for i, pdb_file in enumerate(pdb_files):
    print(f"Processing file {i+1}/{len(pdb_files)}: {os.path.basename(pdb_file)}")
    try:
        # Reset models
        cmd(session, "close")

        # Load structure
        cmd(session, f"open \"{pdb_file}\"")

        # Background (
        cmd(session, "set bgColor white")

        # Backbone cartoon in tan/beige
        cmd(session, "cartoon")
        cmd(session, "cartoon style modeHelix default")
        cmd(session, "color tan target c")

        # Atomistic nucleotides (
        cmd(session, "nucleotides atoms")
        cmd(session, "show nucleic")

        # Ensure hydrogens are present and visible 
        cmd(session, "addh")

        # Sticks only (no balls), thinner cylinders
        cmd(session, "style nucleic stick")
        cmd(session, "size stickRadius 0.14")   # 0.12–0.16 works well

        # Pure atomistic: do not add base fills or ladder pseudobonds
        # (omit: nucleotides fill / nucleotides ladder)

        # Color by element to match standard chemistry scheme
        cmd(session, "color byelement")

        # View & framing
        cmd(session, "view")
        cmd(session, "zoom 0.85")

        # Lighting & outlines for clarity on dark background
        cmd(session, "lighting soft")
        cmd(session, "lighting shadows true")
        cmd(session, "graphics silhouettes true width 2")
        cmd(session, "lighting depthCue true")
        cmd(session, "graphics quality 8192")

        # Save frame
        output_file = os.path.join(output_folder, f'frame{i:04d}.png')
        cmd(session, f"save \"{output_file}\" width 1920 height 1080 supersample 3 transparentBackground false")

        print(f"  Saved: {os.path.basename(output_file)}")
        successful_saves += 1
    except Exception as e:
        print(f"  Error processing {pdb_file}: {e}")
        continue

print(f"\nCompleted! Successfully generated {successful_saves}/{len(pdb_files)} screenshots in {output_folder}")

# Exit when done
if successful_saves > 0:
    cmd(session, "exit")

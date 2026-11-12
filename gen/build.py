"""Build the schematics: writes svg/NN.svg and png/NN.png.

Usage:  python gen/build.py [--out DIR] [N ...]
DIR defaults to the repository root (the parent of gen/). With no numbers, all 88 are built.
"""
import argparse, importlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reg import REG
MODS = ['c_basic', 'c_gen', 'c_proc1', 'c_proc2', 'c_proc3', 'c_proc4']
for m in MODS:
    importlib.import_module(m)

ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument('--out', default=os.path.dirname(HERE), help='output directory (default: repo root)')
ap.add_argument('nums', nargs='*', type=int, help='circuit numbers to build (default: all)')
args = ap.parse_args()
OUT = os.path.abspath(args.out)
os.makedirs(f'{OUT}/svg', exist_ok=True); os.makedirs(f'{OUT}/png', exist_ok=True)

import matplotlib.pyplot as plt
for n in args.nums or sorted(REG):
    c = REG[n]
    s, notes = c['fn']()
    s.finish(f'{OUT}/svg/{n:02d}', c['title'], notes)
    os.replace(f'{OUT}/svg/{n:02d}.png', f'{OUT}/png/{n:02d}.png')
    plt.close('all')
    print('built', n, c['title'])

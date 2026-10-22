#!/usr/bin/env python3
"""Check all four public frozen EEG recordings without fitting."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[1] / 'data/eeg/verify_eeg_all.py'), run_name='__main__')

#!/usr/bin/env python3
"""Rebuild the five approved manuscript figures from archived inputs; no fits."""
from pathlib import Path
import subprocess, sys, shutil
ROOT=Path(__file__).resolve().parents[1]
specs=[(1,'draw_figure1.py','Figure1_HP_GSBS','figure1_algorithm'),
       (2,'draw_figure2.py',None,'figure2_consistency'),
       (3,'draw_eeg_application.py','Figure_EEG_application','figure3_eeg_application'),
       (4,'draw_figure3.py','Figure3_HP_GSBS','figure4_performance'),
       (5,'draw_figure4.py','Figure4_HP_GSBS','figure5_practical')]
for number, script, source, target in specs:
    folder=ROOT/'figure_sources'/f'figure{number}'
    subprocess.run([sys.executable,str(folder/script)],check=True,cwd=folder)
    if source:
        for ext in ('pdf','svg','png'):
            shutil.copy2(folder/f'{source}.{ext}',ROOT/'figures'/f'{target}.{ext}')
    print(f'Figure {number}: {target}',flush=True)

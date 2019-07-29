#!/usr/bin/env python3

from pathlib import Path
import subprocess
import shutil

BASE_PATH = Path('/srv/prj/hit2gap/bemserver/')

PTREPACK = BASE_PATH / 'venv-hit2gap-platform-core/bin/ptrepack'

HDF5_DIR = BASE_PATH / 'hdf5'
TMP_DIR = BASE_PATH / 'tmp_dir_repack'
TMP_DIR.mkdir(exist_ok=True)


for p in HDF5_DIR.rglob("*.hdf5"):
    old_path = p.resolve()
    # Can't resolve if path does not exist with Python < 3.6
    # https://docs.python.org/3.5/library/pathlib.html#pathlib.Path.resolve
    # https://docs.python.org/3.6/library/pathlib.html#pathlib.Path.resolve
    tmp_path = TMP_DIR / p.relative_to(HDF5_DIR)
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_path.parent.resolve() / tmp_path.name

    res = subprocess.run(
        [str(PTREPACK), str(old_path), '-o', str(tmp_path), '--complevel=9'])


shutil.rmtree(str(HDF5_DIR))
TMP_DIR.replace(HDF5_DIR)

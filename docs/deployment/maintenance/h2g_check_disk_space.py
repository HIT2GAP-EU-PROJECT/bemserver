#!/usr/bin/python3

import shutil
import subprocess


M_BYTES = 1024 * 1024
G_BYTES = 1024 * M_BYTES

THRESHOLD_REPACK = 10 * G_BYTES
THRESHOLD_MAINTENANCE = 2 * G_BYTES

REPACK_SCRIPT_PATH = '/srv/prj/hit2gap/bemserver/repack.sh'
MAINTENANCE_SCRIPT_PATH = '/srv/prj/hit2gap/bemserver/set_maintenance_mode.sh'


# If free space too low, repack.
_, _, free = shutil.disk_usage('/')
if free < THRESHOLD_REPACK:

    print('Free disk space < {} Go. Repack.'.format(THRESHOLD_REPACK))
    # If repack in progress, this will fail thanks to the lock file.
    subprocess.run([REPACK_SCRIPT_PATH])

# Recompute free space. If too low, maintenance.
_, _, free = shutil.disk_usage('/')
if free < THRESHOLD_MAINTENANCE:

    print('Free disk space < {} Go. Maintenance.'.format(THRESHOLD_MAINTENANCE))
    # If repack in progress, this won't do anything.
    # Worst case scenario, the app will be set to maintenance next time this script runs.
    subprocess.run([MAINTENANCE_SCRIPT_PATH])

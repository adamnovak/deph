#!/usr/bin/env python3

import sys
import os
import time
import random
import socket
from datetime import datetime
import collections

if len(sys.argv) != 2:
    sys.stderr.write("Specify a target base directory\n")
    sys.exit(1)

base_dir = sys.argv[1]

sys.stderr.write(f"Start on {socket.gethostname()} at {datetime.now()}\n")

os.makedirs(base_dir, exist_ok=True)

target_file = os.path.join(base_dir, "target.dat")

end_time = time.time() + (36 * 60 * 60)

iteration_count = 0
replaced_count_early = 0
replaced_count_late = 0
deleted_count = 0
vanished_count = 0

open_errors = collections.Counter()
errors = collections.Counter()

while time.time() < end_time:
    try:
        # Try to create the file, ignoring if it exists or not.
        fd = os.open(target_file, os.O_CREAT | os.O_WRONLY)
    except Exception as e:
        # Found an error. Record it.
        error_key = str(e)
        if open_errors[error_key] == 0:
            sys.stderr.write(f"{socket.gethostname()}: new file opening error: {error_key}\n")
        open_errors[error_key] += 1
        # Don't try and go on if we couldn't open the file
        continue

    try:

        # Get the stats from the open file
        fd_stats = os.fstat(fd)

        try:
            # And get the stats for the name in the directory
            path_stats = os.stat(target_file)
        except FileNotFoundError:
            path_stats = None

        if path_stats is None or fd_stats.st_dev != path_stats.st_dev or fd_stats.st_ino != path_stats.st_ino:
            replaced_count_early += 1

        time.sleep(random.random() * 0.0001)

        try:
            path_stats = os.stat(target_file)
        except FileNotFoundError:
            path_stats = None

        if path_stats is None or fd_stats.st_dev != path_stats.st_dev or fd_stats.st_ino != path_stats.st_ino:
            replaced_count_late += 1
            
        if path_stats is not None:
            try:
                # Unlink the file
                os.unlink(target_file)
                deleted_count += 1
            except FileNotFoundError:
                vanished_count += 1
    
    except Exception as e:
        # Found an error. Record it.
        error_key = str(e)
        if errors[error_key] == 0:
            sys.stderr.write(f"{socket.gethostname()}: new error: {error_key}\n")
        errors[error_key] += 1
    finally:    
        os.close(fd)

    time.sleep(random.random() * 0.0001)

    iteration_count += 1

sys.stderr.write(f"{socket.gethostname()}: {iteration_count} iterations, {replaced_count_early} times file replaced early, {replaced_count_late} times file replaced late, {deleted_count} successful deletions, {vanished_count} times file vanished\n")
for k, v in open_errors.items():
    sys.stderr.write(f"{socket.gethostname()}: when opening: {v} instances of error: {k}\n")
for k, v in errors.items():
    sys.stderr.write(f"{socket.gethostname()}: {v} instances of error: {k}\n")
    



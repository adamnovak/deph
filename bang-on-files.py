#!/usr/bin/env python3

import sys
import os
import time
import random
import socket
import fcntl
from datetime import datetime
import collections
import signal

if len(sys.argv) != 4:
    sys.stderr.write("Specify 'lock' or 'nolock', a runtime, and a target base directory\n")
    sys.exit(1)

if sys.argv[1] not in ("lock", "nolock"):
    sys.stderr.write("First argument must be 'lock' or 'nolock'\n")
    sys.exit(1)

lock_mode = sys.argv[1]
do_locks = lock_mode == "lock"
runtime_seconds = float(sys.argv[2])
base_dir = sys.argv[3]

do_wait = False

name = f"{socket.gethostname()} {os.getpid()}"

sys.stderr.write(f"{name}: Start at {datetime.now()} in {lock_mode} mode, for {runtime_seconds} seconds\n")

os.makedirs(base_dir, exist_ok=True)

target_file = os.path.join(base_dir, "target.dat")

end_time = time.time() + runtime_seconds

do_alarm = False
if do_alarm:
    # Make sure we don't get stuck waiting forever for a lock
    signal.setitimer(signal.ITIMER_REAL, runtime_seconds + 20)

iteration_count = 0
replaced_count_early = 0
replaced_count_late = 0
deleted_count = 0
vanished_count = 0

open_errors = collections.Counter()
errors = collections.Counter()

locked = False

while time.time() < end_time:
    try:
        # Try to create the file, ignoring if it exists or not.
        fd = os.open(target_file, os.O_CREAT | os.O_WRONLY)
    except Exception as e:
        # Found an error. Record it.
        error_key = str(e)
        if open_errors[error_key] == 0:
            sys.stderr.write(f"{name}: new file opening error: {error_key}\n")
        open_errors[error_key] += 1
        # Don't try and go on if we couldn't open the file
        continue

    try:

        if do_locks:
            # Wait until we can exclusively lock it.
            fcntl.lockf(fd, fcntl.LOCK_EX)
            locked = True

        # Get the stats from the open file
        fd_stats = os.fstat(fd)

        try:
            # And get the stats for the name in the directory
            path_stats = os.stat(target_file)
        except FileNotFoundError:
            path_stats = None

        if path_stats is None or fd_stats.st_dev != path_stats.st_dev or fd_stats.st_ino != path_stats.st_ino:
            replaced_count_early += 1
            continue

        if do_wait:
            time.sleep(random.random() * 0.0001)

        try:
            path_stats = os.stat(target_file)
        except FileNotFoundError:
            path_stats = None

        if path_stats is None or fd_stats.st_dev != path_stats.st_dev or fd_stats.st_ino != path_stats.st_ino:
            replaced_count_late += 1
            # Keep going because Toil does

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
            sys.stderr.write(f"{name}: new error: {error_key}\n")
        errors[error_key] += 1
    finally:
        if locked:
            try:
                fcntl.lockf(fd, fcntl.LOCK_UN)
            except Exception as e:
                # Found an error. Record it.
                error_key = str(e)
                if errors[error_key] == 0:
                    sys.stderr.write(f"{name}: new error: {error_key}\n")
                errors[error_key] += 1
        os.close(fd)

    if do_wait:
        time.sleep(random.random() * 0.0001)

    iteration_count += 1

extra_time = time.time() - end_time

sys.stderr.write(f"{name}: {iteration_count} iterations, {replaced_count_early} times file replaced early, {replaced_count_late} times file replaced late, {deleted_count} successful deletions, {vanished_count} times file vanished, {extra_time} extra seconds\n")
for k, v in open_errors.items():
    sys.stderr.write(f"{name}: when opening: {v} instances of error: {k}\n")
for k, v in errors.items():
    sys.stderr.write(f"{name}: {v} instances of error: {k}\n")
    

# Copyright (C) 2015-2021 Regents of the University of California
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

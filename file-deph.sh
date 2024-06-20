#!/bin/bash
#SBATCH -J file_deph
#SBATCH --nodes=10
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1

# Run with: sbatch --output=output.txt file-deph.sh [lock|nolock] 10 ./testdir
srun ./bang-on-files.py ${1} ${2} ${3}

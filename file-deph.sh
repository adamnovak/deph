#!/bin/bash
#SBATCH -J file_deph
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1

# Run with: sbatch --output=output.txt file-deph.sh ./testdir
srun ./bang-on-files.py ${1}

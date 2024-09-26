#!/bin/bash
#SBATCH --job-name=tfm           # Job name
#SBATCH --nodelist=hpc-gpu4
#SBATCH --nodes=1                    # -N Run all processes on a single node   
#SBATCH --ntasks=1                   # -n Run a single task   
#SBATCH --cpus-per-task=32            # -c Run 1 processor per task       
#SBATCH --gres=gpu:A100_80:1
##SBATCH --constraint=cpu_amd     
#SBATCH --mem=40G                    # Job memory request
#SBATCH --time=00:40:00              # Time limit hrs:min:sec
#SBATCH --qos=regular                 # Cola
#SBATCH --output=log_%x_%j.log       # Standard output and error log


source ~/.bashrc
conda init bash
conda activate myTrecEnv
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
python main.py


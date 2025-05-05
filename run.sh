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

#python plot_rbo.py stats/run_evals/runs_2019 2019 --mode=single
#python plot_rbo.py stats/run_evals/runs_2022 2022 --mode=single
python confussion.py matrix runs/runs_v1 2021 stats/matrices/matrix_v1
python confussion.py matrix runs/runs_v2 2021 stats/matrices/matrix_v2

#!/bin/bash
#SBATCH --job-name=tfm           # Job name
#SBATCH --nodelist=hpc-gpu1
#SBATCH --nodes=1                    # -N Run all processes on a single node
#SBATCH --ntasks=1                   # -n Run a single task
#SBATCH --cpus-per-task=32            # -c Run 1 processor per task
#SBATCH --gres=gpu:A100_80:1
##SBATCH --constraint=cpu_amd
#SBATCH --mem=40G                    # Job memory request
#SBATCH --time=00:30:00              # Time limit hrs:min:sec
#SBATCH --qos=regular                 # Cola
#SBATCH --output=log_%x_%j.log       # Standard output and error log


source ~/.bashrc
conda init bash
conda activate myTrecEnv
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

nohup start_ollama.sh &

#ptyhon get_runs --year <year> <prompt_file> <output_folder/file> <topics (101,102,... or all)> --model <gpt|llama3>
python get_runs.py --year 2021 resources/prompts/DesDelStr_2021.txt runs/DesDelStr_2021_llama3 all --model llama3
#python get_runs.py --year 2021 resources/prompts/DesDelStr_2021.txt runs/DesDelStr_2021 all
#python get_runs.py --year 2021 resources/prompts/DesDelStr_2021.txt runs/DesDelStr_2021 all
#python get_runs.py --year 2022 resources/prompts/prompt_2022.txt runs/runs_2022 all
#python get_runs.py --year 2019 resources/prompts/prompt_2019.txt runs/runs_2019 all

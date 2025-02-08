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

LLM_QRELS_DIR=$(realpath "$1")
TOPICS=$(realpath "$2")
PARTICIPANT_RUNS_DIR=$(realpath "$3")
RUN_EVALS_DIR=stats/run_evals


LLM_DIR_NAME=$(basename "$LLM_QRELS_DIR")
LLM_PARENT_DIR=$(dirname "$LLM_QRELS_DIR")
DERIVED_QRELS_DIR="${LLM_PARENT_DIR}/${LLM_DIR_NAME}_derived"
mkdir -p "$DERIVED_QRELS_DIR"

find "$LLM_QRELS_DIR" -type f | while read -r prompt_qrel_file; do
	# Create directory for derived qrels
	PROMPT_NAME=$(basename "$prompt_qrel_file")
	OUT_DIR=${DERIVED_QRELS_DIR}/${PROMPT_NAME}
	mkdir -p "$OUT_DIR"
	# Obtain derivated qrels for that qrel
	bash misinfo-resources-2021/scripts/gen-2021-derived-qrels.sh "$prompt_qrel_file" "$TOPICS" "$OUT_DIR"


	EVAL_OUT_DIR="${RUN_EVALS_DIR}/${LLM_DIR_NAME}/${PROMPT_NAME}"
	mkdir -p "$EVAL_OUT_DIR"
	# Now obtain the run evaluations using the derived qrels
	bash misinfo-resources-2021/scripts/run-2021-eval.sh "$EVAL_OUT_DIR" "$PARTICIPANT_RUNS_DIR" "$OUT_DIR"
done

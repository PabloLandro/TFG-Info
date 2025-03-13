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

YEAR=$2

# Assign the TOPICS variable based on the year
case "$YEAR" in
    2021)
        TOPICS=$(realpath "misinfo-resources-2021/topics/misinfo-2021-topics.xml")
        ;;
    2022)
        TOPICS=$(realpath "misinfo-resources-2022/topics/misinfo-2022-topics.xml")
        ;;
    2019)
        TOPICS=$(realpath "misinfo-resources-2019/topics/misinfo-2019-topics.xml")
        ;;
    *)
        echo "Error: Unsupported year $YEAR"
        exit 2
        ;;
esac

PARTICIPANT_RUNS_DIR=$(realpath "resources/participant_runs")/$YEAR
RUN_EVALS_DIR="stats/run_evals"


LLM_DIR_NAME=$(basename "$LLM_QRELS_DIR")
LLM_PARENT_DIR=$(dirname "$LLM_QRELS_DIR")
DERIVED_QRELS_PARENT_DIR="${LLM_PARENT_DIR}/${LLM_DIR_NAME}_derived"

# Cleanup
rm -r "$DERIVED_QRELS_PARENT_DIR"
rm -r "${RUN_EVALS_DIR}/${LLM_DIR_NAME}"
mkdir -p "$DERIVED_QRELS_PARENT_DIR"

find "$LLM_QRELS_DIR" -type f | while read -r prompt_qrel_file; do
	# Create directory for derived qrels
	PROMPT_NAME=$(basename "$prompt_qrel_file")
	DERIVED_QRELS_DIR="${DERIVED_QRELS_PARENT_DIR}/${PROMPT_NAME}"
	mkdir -p "$DERIVED_QRELS_DIR"
	# Obtain derivated qrels for that qrel
	bash misinfo-resources-2021/scripts/gen-2021-derived-qrels.sh "$prompt_qrel_file" "$TOPICS" "$DERIVED_QRELS_DIR"


	EVAL_OUT_DIR="${RUN_EVALS_DIR}/${LLM_DIR_NAME}/${PROMPT_NAME}"

	find "$PARTICIPANT_RUNS_DIR" -type f | while read -r PARTICIPANT_RUN_FILE; do
		RUN_NAME=$(basename "$PARTICIPANT_RUN_FILE")
		mkdir -p "${EVAL_OUT_DIR}/${RUN_NAME}"
		# Now obtain the run evaluations using the derived qrels
		#bash misinfo-resources-2021/scripts/run-2021-eval.sh "$EVAL_OUT_DIR" "$PARTICIPANT_RUNS_DIR" "$DERIVED_QRELS_DIR"
		# Helpful compatibility
		python misinfo-resources-2021/scripts/compatibility.py "${DERIVED_QRELS_DIR}/misinfo-qrels-graded.helpful-only" "$PARTICIPANT_RUN_FILE" > "${EVAL_OUT_DIR}/${RUN_NAME}/helpful-compatibility.txt"
		# Harmful compatiblity
		python misinfo-resources-2021/scripts/compatibility.py "${DERIVED_QRELS_DIR}/misinfo-qrels-graded.harmful-only" "$PARTICIPANT_RUN_FILE" > "${EVAL_OUT_DIR}/${RUN_NAME}/harmful-compatibility.txt"
	done
done

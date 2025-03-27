#!/bin/bash
#SBATCH --job-name=tfm           # Job name
#SBATCH --nodelist=hpc-gpu4
#SBATCH --nodes=1                # -N Run all processes on a single node
#SBATCH --ntasks=1               # -n Run a single task
#SBATCH --cpus-per-task=32       # -c Run 32 processors per task
#SBATCH --gres=gpu:A100_80:1
#SBATCH --mem=40G                # Job memory request
#SBATCH --time=00:40:00          # Time limit hrs:min:sec
#SBATCH --qos=regular            # Queue
#SBATCH --output=log_%x_%j.log   # Standard output and error log

source ~/.bashrc
conda init bash
conda activate myTrecEnv
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <qrel_file> <year>"
    exit 1
fi

QRELS=$1
YEAR=$2

# Set variables based on the year
case "$YEAR" in
    2019)
        TOPICS="misinfo-resources-2019/topics/misinfo-2019-topics.xml"
        PARTICIPANT_RUNS_DIR=$(realpath "resources/participant_runs/2019")
        ;;
    2020)
        TOPICS="Value for 2020"
        PARTICIPANT_RUNS_DIR=$(realpath "resources/participant_runs/2020")
        ;;
    2021)
        TOPICS="misinfo-resources-2021/topics/misinfo-2021-topics.xml"
        PARTICIPANT_RUNS_DIR=$(realpath "resources/participant_runs/2021")
        ;;
    2022)
        TOPICS="misinfo-resources-2022/topics/misinfo-2022-topics.xml"
        PARTICIPANT_RUNS_DIR=$(realpath "resources/participant_runs/2022/adhoc")
        ;;
    *)
        echo "Invalid year: $YEAR"
        echo "Year must be one of: 2019, 2020, 2021, 2022"
        exit 1
        ;;
esac

RUN_EVALS_DIR="stats/run_evals"
QRELS_DIR=$(dirname "$QRELS")
QRELS_NAME=$(basename "$QRELS")
DERIVED_QRELS="${QRELS_DIR}/${QRELS_NAME}_derived"

# Prepare directories
rm -rf "$DERIVED_QRELS"
mkdir -p "$DERIVED_QRELS"

# Generate derived QRELs
case "$YEAR" in
    2019)
        # No additional processing needed for 2019
        ;;
    2020)
        echo "Processing logic for 2020 not implemented"
        ;;
    2021)
        bash misinfo-resources-2021/scripts/gen-2021-derived-qrels.sh "$QRELS" "$TOPICS" "$DERIVED_QRELS"
        ;;
    2022)
        python misinfo-resources-2022/scripts/gen-qrels-for-compatibility.py --qrels "$QRELS" --output "$DERIVED_QRELS/misinfo-qrels"
        ;;
esac

EVAL_OUT_DIR="${RUN_EVALS_DIR}/${QRELS_NAME}"
mkdir -p "$EVAL_OUT_DIR"

# Perform evaluation
case "$YEAR" in
    2019)
        # No evaluation needed for 2019
        ;;
    2020)
        echo "Evaluation logic for 2020 not implemented"
        ;;
    2021)
        find "$PARTICIPANT_RUNS_DIR" -type f | while read -r PARTICIPANT_RUN_FILE; do
            RUN_NAME=$(basename "$PARTICIPANT_RUN_FILE")
            mkdir -p "${EVAL_OUT_DIR}/${RUN_NAME}"
            # Helpful compatibility
            python misinfo-resources-2021/scripts/compatibility.py "${DERIVED_QRELS}/misinfo-qrels-graded.helpful-only" "$PARTICIPANT_RUN_FILE" > "${EVAL_OUT_DIR}/${RUN_NAME}/helpful-compatibility.txt"
            # Harmful compatibility
            python misinfo-resources-2021/scripts/compatibility.py "${DERIVED_QRELS}/misinfo-qrels-graded.harmful-only" "$PARTICIPANT_RUN_FILE" > "${EVAL_OUT_DIR}/${RUN_NAME}/harmful-compatibility.txt"
        done
        ;;
    2022)
        bash misinfo-resources-2022/scripts/run-eval.sh "$EVAL_OUT_DIR" "$DERIVED_QRELS"
        ;;
esac


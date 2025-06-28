import os, argparse, sys
from trec_utils import set_year, get_year_data, get_stats, read_line_from_qrel
import numpy as np
import matplotlib.pyplot as plt


POS_VALS = [1,2]

def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def get_filtered_runs(run_file, qrels, year):
    runs = {}
    with open(run_file, "r") as file:
        for line in file:
            doc_run = read_line_from_qrel(line)
            topic_id = doc_run["topic_id"]
            doc_id = doc_run["doc_id"]
            if not doc_id in qrels[topic_id]:
                continue
            if topic_id not in runs:
                runs[topic_id] = {}
            runs[topic_id][doc_id] = doc_run
    return runs

def get_kappa(confussion_matrix):
    N = 0
    for (real,pred),count in confussion_matrix.items():
        N = N + count

    # get agreement
    a = 0
    for i in [0,1,2]:
        if (i,i) in confussion_matrix:
            a = a + confussion_matrix[(i,i)]

    # get expected frequency
    ef = 0
    for i in [0,1,2]:
        column_count = 0
        row_count = 0
        for k in [0,1,2]:
            if (i,k) in confussion_matrix:
                column_count = column_count + confussion_matrix[(i,k)]
            if (k,i) in confussion_matrix:
                row_count = row_count + confussion_matrix[(k,i)]
        ef = ef + (column_count*row_count/N)

    kappa = (a-ef) / (N-ef)

    return kappa

def get_mae_old(TP,FP,FN,TN):
    return (FP + FN) / (TP + FP + FN + TN)

def get_mae(confussion_matrix):
    N = 0
    for (real,pred),count in confussion_matrix.items():
        N = N + count

    # get agreement
    a = 0
    for i in [0,1,2]:
        a = a + confussion_matrix[(i,i)]
    return (N-a)/N

def get_confidence_interval(TP, FP, FN, TN, get_feature, bootstraps=20):
    feature_values = []
    arr = np.array(["TP"]*TP + ["FP"]*FP + ["FN"]*FN + ["TN"]*TN)
    for _ in range(bootstraps):
        indices = np.random.choice(len(arr), size=len(arr), replace=True)
        bootstrap = arr[indices]
        TP2 = np.sum(bootstrap == "TP")
        FP2 = np.sum(bootstrap == "FP")
        FN2 = np.sum(bootstrap == "FN")
        TN2 = np.sum(bootstrap == "TN")
        feature_values.append(get_feature(TP2, FP2, FN2, TN2))
    out = {}
    out["lb"] = np.percentile(feature_values, 2.5)
    out["ub"] = np.percentile(feature_values, 97.5)
    return out

def get_kappa_old(TP,FP,FN,TN):
    N = TP + FP + FN + TN
    p0 = (TP + TN) / N
    possitive_agreement = (TP + FN) * (TP + FP) / (N**2) 
    negative_agreement = (TN + FN) * (TN + FP) / (N**2)
    pe = possitive_agreement + negative_agreement
    if pe == 1:
        print(TP,FP,FN,TN)
    if pe == 1:
        return 0
    kappa = (p0 - pe) / (1 - pe)
    return kappa

def get_stats_from_folder(folder, qrels, year):
    runs = get_filtered_runs(folder, qrels, year)
    out = {}
    stats = get_stats()
    for stat in stats:
        TP, FP, FN, TN = get_confussion(stat, POS_VALS, runs, qrels)
        confussion_matrix = get_confusion2(stat, runs, qrels)
        out[stat] = {}
        out[stat]["kappa"] = get_kappa(confussion_matrix)
        out[stat]["kappa_interval"] = get_confidence_interval(TP, FP, FN, TN, get_kappa_old)
        out[stat]["mae"] = get_mae(confussion_matrix)
        out[stat]["mae_interval"] = get_confidence_interval(TP, FP, FN, TN, get_mae_old)
    return out

def get_confussion(stat, pos_vals, runs, qrels):
    TP = 0
    FP = 0
    FN = 0
    TN = 0

    for topic_id in runs:
        for doc_id in runs[topic_id]:
            # If there is not a qrel for that doc_id, we skip
            if doc_id not in qrels[topic_id]:
                continue

            real = qrels[topic_id][doc_id][stat]
            pred = runs[topic_id][doc_id][stat]

            if real is None or pred is None:
                continue

            if real in pos_vals:
                if pred in pos_vals:
                    TP += 1
                else:
                    FN += 1
            else:
                if pred in pos_vals:
                    FP += 1
                else:
                    TN += 1
    if stat == "cr":
        print(TP,FP,FN,TN)
    return  TP,FP,FN,TN

def get_confusion2(stat, runs, qrels):
    confusion_matrix = {}

    for i in [0,1,2]:
        for j in [0,1,2]:
            confusion_matrix[(i,j)] = 0

    for topic_id in runs:
        for doc_id in runs[topic_id]:
            # If there is no qrel for that doc_id, we skip
            if doc_id not in qrels[topic_id]:
                continue

            real = qrels[topic_id][doc_id][stat]
            pred = runs[topic_id][doc_id][stat]

            if real is None or pred is None:
                continue

            # Increment the count for the (real, pred) pair
            confusion_matrix[(real, pred)] = confusion_matrix.get((real, pred), 0) + 1

    return confusion_matrix

def plot_confusion_matrix(confusion_matrix, labels, name):
    # Create a matrix of zeros with shape (len(labels), len(labels))
    matrix = np.zeros((len(labels), len(labels)))

    for (real, pred), count in confusion_matrix.items():
        matrix[real, pred] = count

    plt.figure(figsize=(8, 6))
    plt.imshow(matrix, cmap="Blues", interpolation="nearest")
    plt.colorbar(label="Count")

    # Add labels for axes
    plt.xticks(ticks=np.arange(len(labels)), labels=labels, fontsize=14)
    plt.yticks(ticks=np.arange(len(labels)), labels=labels, fontsize=14)
    plt.xlabel("Etiqueta Verdadera", fontsize=14)
    plt.ylabel("Etiqueta GPT", fontsize=14)
    plt.title(f"Matriz de confusión {name}", fontsize=14)

    # Add annotations to each cell
    for i in range(len(labels)):
        for j in range(len(labels)):
            plt.text(j, i, str(matrix[i, j]), ha='center', va='center', fontsize=16, color="black")

    plt.tight_layout()
    plt.show()

def validate_input(mode, input_path, year, output_path):
    if mode == "table" and not os.path.isdir(input_path):
        sys.exit(f"Error: For mode 'table', input must be a folder. '{input_path}' is not a valid folder.")
    if mode == "matrix" and not os.path.isfile(input_path):
        sys.exit(f"Error: For mode 'matrix', input must be a file. '{input_path}' is not a valid file.")
    if mode == "table" and not os.path.isdir(output_path):
        sys.exit(f"Error: For mode 'table', output must be a folder. '{output_path}' is not a valid folder.")
    if mode == "matrix" and not os.path.isfile(output_path):
        sys.exit(f"Error: For mode 'matrix', output must be a file. '{output_path}' is not a valid file.")
    if year not in [2019, 2020, 2021, 2022]:
        sys.exit(f"Error: Year must be one of 2019, 2020, 2021, 2022. Provided: {year}")

def generate_confussion_matrix(qrels, input_file, output, year):
    runs = get_filtered_runs(input_file, qrels, year)
    stats = get_stats()
    with open(output, "w") as out_file:
        for stat in stats.keys():
            confusion_matrix = get_confusion2(stat, runs, qrels)
            plot_confusion_matrix(confusion_matrix, [0,1,2], stats[stat]["name"])
            MAE = get_mae(confusion_matrix)
            print(f"MAE: {MAE}\n")

            kappa = get_kappa(confusion_matrix)
            print(f"Cohen´s Kapa: {kappa}\n")
        

def generate_tables(qrels, input_folder, output, year):
    stats = {}

    for combination in os.listdir(input_folder):
        stats[combination] = get_stats_from_folder(os.path.join(input_folder, combination), qrels, year)

    for stat in ["u", "s", "cr"]:
        with open(output + stat, "w") as file:
            file.write(f"Table for {stat}\n")
            file.write("Prompt features\t\t\tMAE\t\t\tCohen's Kappa\n")
            #for combination in ["Nothing", "Rol", "Des", "Nar", "Del", "Str", "RolDes", "RolNar", "RolDel", "RolStr", "DesNar", "DesDel", "DesStr", "NarDel", "NarStr", "DelStr", "RolDesNar", "RolDesDel", "RolDesStr", "RolNarDel", "RolNarStr", "RolDelStr", "DesNarDel", "DesNarStr", "NarDelStr", "RolDesNarDel", "RolDesNarStr", "RolDesDelStr", "RolNarDelStr", "DesNarDelStr", "RolDesNarDelStr"]:
            for combination in stats:
                if stats[combination] is None or stat not in stats[combination]:
                    file.write(f"{combination}\t\t\tErroro\t\t\tErroro\n")
                else:
                    mae = stats[combination][stat]["mae"]
                    mae_interval = stats[combination][stat]["mae_interval"]
                    mae_margin = max(mae-mae_interval["lb"], mae_interval["ub"] - mae)
                    kappa = stats[combination][stat]["kappa"]
                    kappa_interval = stats[combination][stat]["kappa_interval"]
                    kappa_margin = max(kappa-kappa_interval["lb"], kappa_interval["ub"] - kappa)
                    file.write(f"{combination:<12}&{mae:.2f}$\\pm${mae_margin:.2f}&{kappa:.2f}$\\pm${kappa_margin:.2f}\\\\\n")

def main():
    parser = argparse.ArgumentParser(description="Process input based on mode and year.")
    parser.add_argument(
        "mode",
        choices=["matrix", "table"],
        help="Mode of operation. 'matrix' requires a directory and a file prefix (output will add stat name to the prefix), 'table' requires a folder."
    )
    parser.add_argument(
        "input",
        help="Input file (for matrix) or folder (for table)."
    )
    parser.add_argument(
        "year",
        type=int,
        help="Year of data to use. Must be one of: 2019, 2020, 2021, 2022."
    )
    parser.add_argument(
        "output",
        help="Path to output folder."
    )

    args = parser.parse_args()

    # Validate the input based on mode
    validate_input(args.mode, args.input, args.year, args.output)

    set_year(args.year)

    # Get year-specific data
    qrels,_ = get_year_data(with_graded_usefulness=True)

    # Perform actions based on mode
    if args.mode == "matrix":
        generate_confussion_matrix(qrels, args.input, args.output, args.year)
    elif args.mode == "table":
        generate_tables(qrels, args.input, args.output, args.year)

if __name__ == "__main__":
    main()

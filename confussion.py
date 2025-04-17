import os, argparse, sys
from trec_utils import set_year, get_year_data, get_stats, read_line_from_qrel
import numpy as np

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

def get_kappa(TP,FP,FN,TN):
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


def get_mae(TP,FP,FN,TN):
    return (FP + FN) / (TP + FP + FN + TN)

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

def get_stats_from_folder(folder, qrels, year):
    runs = get_filtered_runs(folder, qrels, year)
    out = {}
    stats = get_stats()
    for stat in stats:
        TP, FP, FN, TN = get_confussion(stat, POS_VALS, runs, qrels)
        out[stat] = {}
        out[stat]["kappa"] = get_kappa(TP, FP, FN, TN)
        out[stat]["kappa_interval"] = get_confidence_interval(TP, FP, FN, TN, get_kappa)
        out[stat]["mae"] = get_mae(TP, FP, FN, TN)
        out[stat]["mae_interval"] = get_confidence_interval(TP, FP, FN, TN, get_mae)
    return out

def write_confussion(stat, pos_vals, name, runs, qrels, file):
    
    TP, FP, FN, TN = get_confussion(stat, pos_vals, runs, qrels)
    print(f"{TP} {FP} {FN} {TN}")
    file.write(f"\n{name} confussion matrix:\n")
    file.write(f"TP={TP}\tFP={FP}\tFN={FN}\tTN={TN}\n")

    precision = TP / (TP+FP)
    file.write(f"Precision: {precision}\n")

    MAE = get_mae(TP, FP, FN, TN)
    file.write(f"MAE: {MAE}\n")

    kappa = get_kappa(TP, FP, FN, TN)
    file.write(f"Cohen´s Kapa: {kappa}\n")

    recall = TP / (TP + FN)
    file.write(f"Recall: {recall}\n\n")

    latex_table = f"""
        \\begin{{table}}[]
        \\begin{{tabular}}{{|c|ccc|}}
        \\hline
        {name}            & \\multicolumn{{3}}{{c|}}{{Predicción}}                                          \\\\ \\hline
                                & \\multicolumn{{1}}{{c|}}{{}}         & \\multicolumn{{1}}{{c|}}{{Positivo}} & Negativo \\\\ \\hline
        \\multirow{{2}}{{*}}{{Actual}} & \\multicolumn{{1}}{{c|}}{{Positivo}} & \\multicolumn{{1}}{{c|}}{{{TP}}}       & {FN}       \\\\ \\cline{{2-4}} 
                                & \\multicolumn{{1}}{{c|}}{{Negativo}} & \\multicolumn{{1}}{{c|}}{{{FP}}}       & {TN}       \\\\ \\hline
        \\end{{tabular}}
        \\end{{table}}
        """
    file.write(latex_table)



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
            write_confussion(stat, stats[stat]["pos_vals"], stats[stat]["name"], runs, qrels, out_file)
        

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
                    file.write(f"{combination:<12}&{mae:.2f}$pm${mae_margin:.2f}&{kappa:.2f}$pm${kappa_margin:.2f}\\\\\n")

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
    qrels,_,_ = get_year_data(with_graded_usefulness=True)

    # Perform actions based on mode
    if args.mode == "matrix":
        generate_confussion_matrix(qrels, args.input, args.output, args.year)
    elif args.mode == "table":
        generate_tables(qrels, args.input, args.output, args.year)

if __name__ == "__main__":
    main()

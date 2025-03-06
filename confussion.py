import os
from trec_utils import get_qrels_dict, get_qrels_dict_all, preprocess_run
import numpy as np

POS_VALS = [1,2]

# Load the qrel runs into;q a dictionary indexed by topic_id
qrels = get_qrels_dict_all()

def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def get_filtered_runs(run_folder):
    runs = {}
    # Iterate over every topic run file
    for topic_id in os.listdir(run_folder):
        if not is_int(topic_id):
            continue
        run = {}
        with open(os.path.join(run_folder, topic_id), "r") as file:
            count = 0
            for line in file:
                doc_run = {}

                # Read every doc_run for this topic
                doc_run["doc_id"], doc_run["u"], doc_run["s"], doc_run["cr"] = line.split(" ")
                # If there is not qrel run for this document, we skip it
                if not doc_run["doc_id"] in qrels[topic_id]:
                    #print("Doc not found in qrels")
                    continue
                count += 1
                # Add correctiveness and preference
                preprocess_run(doc_run)
                run[doc_run["doc_id"]] = doc_run
            #print(f"{topic_id} valid: {count}")
        runs[topic_id] = run
        # Check if there is any document missing
        missing_docs = 0
        for doc_id in qrels[topic_id]:
            if doc_id not in run:
                missing_docs += 1
        if missing_docs > 0:
            #print(f"WARN: Missing {missing_docs} documents for topic {topic_id}")
            pass
    return runs

def get_kappa(TP,FP,FN,TN):
    N = TP + FP + FN + TN
    p0 = (TP + TN) / N
    possitive_agreement = (TP + FN) * (TP + FP) / (N**2) 
    negative_agreement = (TN + FN) * (TN + FP) / (N**2)
    pe = possitive_agreement + negative_agreement
    if pe == 1:
        print(TP,FP,FN,TN)
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

def get_confussion(stat, pos_vals, runs):
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

def get_stats_from_folder(folder):
    runs = get_filtered_runs(folder)
    out = {}
    for stat in ["u", "cr", "s"]:
        TP, FP, FN, TN = get_confussion(stat, POS_VALS, runs)
        out[stat] = {}
        out[stat]["kappa"] = get_kappa(TP, FP, FN, TN)
        out[stat]["kappa_interval"] = get_confidence_interval(TP, FP, FN, TN, get_kappa)
        out[stat]["mae"] = get_mae(TP, FP, FN, TN)
        out[stat]["mae_interval"] = get_confidence_interval(TP, FP, FN, TN, get_mae)
    return out

def print_confussion(stat, pos_vals, name, runs):
    
    TP, FP, FN, TN = get_confussion(stat, pos_vals, runs)

    print(f"\n{name} confussion matrix:")
    print(f"TP={TP}\tFP={FP}\tFN={FN}\tTN={TN}")

    precision = TP / (TP+FP)
    print(f"Precision: {precision}")

    MAE = get_mae(TP, FP, FN, TN)
    print(f"MAE: {MAE}")

    kappa = get_kappa(TP, FP, FN, TN)
    print(f"Cohen´s Kapa: {kappa}")

    recall = TP / (TP + FN)
    print(f"Recall: {recall}\n")

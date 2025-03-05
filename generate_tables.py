import os
from confussion import get_stats_from_folder

RUNS_FOLDER = "runs_features_v1"
OUTPUT_FILE = "tables_"


stats = {}

for combination in os.listdir(os.path.join("runs", RUNS_FOLDER)):
    stats[combination] = get_stats_from_folder(os.path.join("runs", RUNS_FOLDER, combination))

for stat in ["u", "s", "cr"]:
    with open(OUTPUT_FILE + stat, "w") as file:
        file.write(f"Table for {stat}\n")
        file.write("Prompt features\t\t\tMAE\t\t\tCohen's Kappa\n")
        for combination in ["Nothing", "Rol", "Des", "Nar", "Del", "Str", "RolDes", "RolNar", "RolDel", "RolStr", "DesNar", "DesDel", "DesStr", "NarDel", "NarStr", "DelStr", "RolDesNar", "RolDesDel", "RolDesStr", "RolNarDel", "RolNarStr", "RolDelStr", "DesNarDel", "DesNarStr", "NarDelStr", "RolDesNarDel", "RolDesNarStr", "RolDesDelStr", "RolNarDelStr", "DesNarDelStr", "RolDesNarDelStr"]:
        #for combination in stats:
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


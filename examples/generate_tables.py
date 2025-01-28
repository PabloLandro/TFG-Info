import sys
import os
sys.path.append(os.getcwd())
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
        for combination in stats:
            if stats[combination] is None or stat not in stats[combination]:
                file.write(f"{combination}\t\t\tErroro\t\t\tErroro\n")
            else:
                file.write(f"{combination}\t\t\t{stats[combination][stat]['mae']}\t\t\t{stats[combination][stat]['kappa']}\n")


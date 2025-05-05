# File paths
file1_path = "misinfo-resources-2022/qrels/qrels.final.oct-19-2022"
file2_path = "runs/runs_2022"

# Load files into dictionaries
def load_file(file_path):
    data = {}
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split()
            key = " ".join(parts[:-2])  # Use everything except the last two numbers as the key
            data[key] = (int(parts[-2]), int(parts[-1]))
    return data

file1_data = load_file(file1_path)
file2_data = load_file(file2_path)

# Compare the files
differences = []
for key in file1_data:
    if key in file2_data:
        file1_last = file1_data[key][1]
        file2_last = file2_data[key][1]
        if (file1_last, file2_last) in [(1, 0), (0, 1)]:
            differences.append((key, file1_last, file2_last))

# Output results
if differences:
    print("Lines with mismatched last numbers (1 vs 0 or 0 vs 1):")
    for key, num1, num2 in differences:
        print(f"{key} - File1: {num1}, File2: {num2}")
else:
    print("No differences found.")


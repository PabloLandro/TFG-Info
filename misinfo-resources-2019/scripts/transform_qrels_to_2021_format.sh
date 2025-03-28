#!/bin/bash

# Usefulness and credibility can be treated as is
# Supportiveness on the other hand is offset, so we must subtract 1 to match the meaning in 2021 qrels.

# Check if the correct number of arguments is passed
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_file> <output_file>"
    exit 1
fi

input_file="$1"
output_file="$2"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: File '$input_file' not found."
    exit 1
fi

# Temporary auxiliary file
temp_file=$(mktemp)

# Process the file and subtract 1 from the 5th column
while IFS= read -r line; do
    # Split the line into columns
    cols=($line)

    # Check if the line has at least 7 columns
    if [ ${#cols[@]} -ne 7 ]; then
        echo "Error: Invalid line format in input file. Each line must have 7 columns."
        rm "$temp_file"  # Clean up the temporary file
        exit 1
    fi

    # Subtract 1 from the 5th column (index 4)
    cols[4]=$((cols[4] - 1))

    # Write the modified line to the temporary file
    echo "${cols[0]} ${cols[1]} ${cols[2]} ${cols[3]} ${cols[4]} ${cols[5]} ${cols[6]}" >> "$temp_file"
done < "$input_file"

# Write the processed content to the output file
mv "$temp_file" "$output_file"

echo "File has been processed. Output written to '$output_file'."

#!/bin/bash

# Ensure the directory is provided
if [ $# -ne 2 ]; then
  echo "Usage: $0 <directory> <output_file>"
  exit 1
fi

directory=$1
output_file=$2

# Clear the output file or create it if it doesn't exist
> "$output_file"

# Process each file in the directory
for file in "$directory"/*; do
  if [[ -f "$file" ]]; then  # Only process regular files
    while IFS= read -r line; do
      echo "$(basename "$file") 0 $line" >> "$output_file"
    done < "$file"
  fi
done

echo "All files from $directory have been collapsed into $output_file."

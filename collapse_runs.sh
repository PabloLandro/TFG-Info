#!/bin/bash

for dir in "$@"; do
  output_file="${dir%/}.txt"  # Remove trailing slash and add .txt
  > "$output_file"  # Create or clear the output file
  echo "Processing directory: $dir"
  for file in "$dir"/*; do
    echo "  Processing file: $file"
    while IFS= read -r line; do
      echo "$(basename "$file") 0 $line" >> "$output_file"
    done < "$file"
  done
done

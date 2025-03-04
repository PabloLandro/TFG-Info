#!/bin/bash

# Check if both URL and DOWNLOAD_DIR are provided as arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <URL> <DOWNLOAD_DIR>"
    exit 1
fi

# Variables
URL="$1"
DOWNLOAD_DIR="$2"
USERNAME="tipster"
PASSWORD="cdroms"
TIMEOUT=10

echo "URL provided: $URL"
echo "Download directory provided: $DOWNLOAD_DIR"

# Step 1: Download the webpage
wget --user="$USERNAME" --password="$PASSWORD" -q -O page.html "$URL"

cat page.html | head -n 20

echo "Step1"

# Step 2: Extract links containing <strong>Input</strong>
LINKS=$(grep -oP '(?<=<a href=")[^"]*(?=.*Input)' page.html)

echo "Extracted links:"
echo "$LINKS"

echo "Step 2"

# Step 3: Download each file
for link in $LINKS; do
    # If the link is relative, make it absolute
    if [[ $link != http* ]]; then
        link="$URL/$link"
    fi

    # Extract the filename from the link
    filename=$(basename "$link")

    # Check if the file already exists in the download directory
    if [[ -f "$DOWNLOAD_DIR/$filename" ]]; then
        echo "File already exists, skipping: $filename"
    else
        # Download the file to the specified directory
        wget --user="$USERNAME" --password="$PASSWORD" -P "$DOWNLOAD_DIR" "$link"
        echo "Downloaded to $DOWNLOAD_DIR: $link"
    fi

    sleep "$TIMEOUT"

done

# Clean up
rm page.html

#!/bin/bash

# Add a <stance> field to every topic based on efficacy values.
# Efficacy values are stored in 2019topics_efficacy.txt:
#   -1 for "treatment not helpful" (unhelpful)
#    0 for "evidence inconclusive" (ignored)
#    1 for "treatment helpful" (helpful)

# Remove topics with inconclusive efficacy (16 topics out of 50).
# Paths to the XML file and efficacy file
TOPICS_FILE="misinfo-resources-2019/topics/misinfo-2019-topics.xml"
EFFICACY_FILE="misinfo-resources-2019/qrels/2019topics_efficacy.txt"

# Backup the original XML file (optional)
cp "$TOPICS_FILE" "${TOPICS_FILE}.bak"

# Process each line of the efficacy file
while read -r line; do
    # Extract the topic number and stance value
    topic_number=$(awk '{print $1}' <<< "$line")
    stance_value=$(awk '{print $2}' <<< "$line")

    # Skip if stance value is 0 (inconclusive)
    if [[ "$stance_value" == "0" ]]; then
    # Remove the entire topic if stance is inconclusive
    sed -i "/<topic>.*<number>$topic_number<\/number>/,/<\/topic>/d" "$TOPICS_FILE"
    continue
    fi

    # Determine the stance label
    case "$stance_value" in
        -1) stance="unhelpful" ;;
        1) stance="helpful" ;;
        *) echo "Unexpected stance value: $stance_value" >&2; exit 1 ;;
    esac

    # Add the <stance> tag to the corresponding topic in the XML
    sed -i "/<topic>.*<number>$topic_number<\/number>/a \ \ \ \ <stance>$stance<\/stance>" "$TOPICS_FILE"

done < "$EFFICACY_FILE"

echo "Processing complete. Updated XML saved to $TOPICS_FILE (backup: ${TOPICS_FILE}.bak)."

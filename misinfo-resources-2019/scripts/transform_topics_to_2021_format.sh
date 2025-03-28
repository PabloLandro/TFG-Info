#!/bin/bash

# We need to add a stance field to every topic.
# The real efficacy of a topic is in 2019topics_efficacy.text:
#   -1 for treatment not helpful
#   0  for evidence inconclusive
#   1  for treatment helpful

# We remove the inconclusive topics (16 topics out of 50 (topic 14 has no qrels))

# Define paths to the XML and the file with stance values
TOPICS_FILE="misinfo-resources-2019/topics/misinfo-2019-topics.xml"
EFFICACY_FILE="misinfo-resources-2019/qrels/2019topics_efficacy.txt"

# Read the stance file and process it line by line
while read -r line; do
  # Extract the topic number and stance value from the file
  topic_number=$(echo "$line" | awk '{print $1}')
  stance_value=$(echo "$line" | awk '{print $2}')

  # Check if the stance value is not zero
  if [[ "$stance_value" != "0" ]]; then
    # Determine the stance based on the value
    if [[ "$stance_value" == "-1" ]]; then
      stance="unhelpful"
    elif [[ "$stance_value" == "1" ]]; then
      stance="helpful"
    fi

    # Add the <stance> tag to the relevant topic in the XML file
    sed -i "/<topic>.*<number>$topic_number<\/number>/a \ \ \ \ <stance>$stance<\/stance>" "$TOPICS_FILE"
  fi
done < "$EFFICACY_FILE"
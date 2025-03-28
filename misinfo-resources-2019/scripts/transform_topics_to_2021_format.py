import xml.etree.ElementTree as ET

# Define paths to the XML and the file with stance values
TOPICS_FILE = "misinfo-resources-2019/topics/misinfo-2019-topics.xml"
EFFICACY_FILE = "misinfo-resources-2019/qrels/2019topics_efficacy.txt"

# Load the efficacy data into a dictionary
stance_map = {
    "1": "helpful",
    "-1": "unhelpful",
    "0": None  # None indicates the topic should be removed
}

efficacy = {}
with open(EFFICACY_FILE, "r") as file:
    for line in file:
        topic_number, stance_value = line.strip().split()
        efficacy[topic_number] = stance_map[stance_value]

# Parse the XML file
tree = ET.parse(TOPICS_FILE)
root = tree.getroot()

# Iterate through topics and modify or remove as needed
for topic in list(root):
    topic_number = topic.find("number").text
    stance = efficacy.get(topic_number)

    if stance is None:
        # Remove topics with inconclusive stance
        root.remove(topic)
    else:
        # Add or update the <stance> tag
        stance_element = topic.find("stance")
        if stance_element is None:
            # Create a new <stance> element if it doesn't exist
            stance_element = ET.Element("stance")
            topic.append(stance_element)
        stance_element.text = stance

# Write the updated XML back to the file
tree.write(TOPICS_FILE, encoding="utf-8", xml_declaration=True)

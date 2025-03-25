import argparse, os, sys
from trec_utils import get_qrels_dict

def create_parser():
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Verify directory and file arguments.")
    
    # Add directory argument
    parser.add_argument(
        "directory",
        type=str,
        help="Path to the directory."
    )
    
    # Add file arguments
    parser.add_argument(
        "--usefulness_run",
        type=str,
        required=True,
        help="Path to the usefulness_run file within the directory."
    )
    parser.add_argument(
        "--supportiveness_run",
        type=str,
        required=True,
        help="Path to the supportiveness_run file within the directory."
    )
    parser.add_argument(
        "--credibility_run",
        type=str,
        required=True,
        help="Path to the credibility_run file within the directory."
    )
    return parser

def validate_args(args):
    # Validate directory
    if not os.path.isdir(args.directory):
        raise ValueError(f"The directory '{args.directory}' does not exist.")
    
    # Validate files
    for file_arg in ["usefulness_run", "supportiveness_run", "credibility_run"]:
        file_path = getattr(args, file_arg)
        full_path = os.path.join(args.directory, file_path)
        if not os.path.isfile(full_path):
            raise ValueError(f"The file '{file_path}' does not exist in the directory '{args.directory}'.")
    
    print("All arguments are valid.")

def main():
    
    parser = create_parser()
    
    # Parse the arguments
    args = parser.parse_args()
    validate_args(args)

    usefulness_dict = get_qrels_dict(os.path.join(args.directory, args.usefulness_run), 2021, skip_unuseful=False)
    supportiveness_dict = get_qrels_dict(os.path.join(args.directory, args.supportiveness_run), 2021, skip_unuseful=False)
    credibility_dict = get_qrels_dict(os.path.join(args.directory, args.credibility_run), 2021, skip_unuseful=False)

    with open(os.path.join(args.directory, "combined"), "w") as file:
        for topic in usefulness_dict:
            if topic not in supportiveness_dict or topic not in credibility_dict:
                print("Missing topic")
                continue
            for doc_id in usefulness_dict[topic]:
                if doc_id not in supportiveness_dict[topic] or doc_id not in credibility_dict[topic]:
                    print("Missing doc")
                    continue
                file.write(f"{topic} 0 {doc_id} {usefulness_dict[topic][doc_id]['u' ]} {supportiveness_dict[topic][doc_id]['s']} {credibility_dict[topic][doc_id]['cr']}")
                file.write("\n")
    

if __name__ == "__main__":
    main()



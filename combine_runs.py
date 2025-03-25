import argparse
import os

def main():
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
    
    # Parse the arguments
    args = parser.parse_args()
    
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

if __name__ == "__main__":
    main()



#!/bin/bash

# Check if a virtual environment is active
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Warning: No virtual environment detected. It's recommended to use a virtual environment."
fi

# Install dependencies without specific versions
pip install -r requirements.txt

# Success message
echo "All dependencies installed successfully."

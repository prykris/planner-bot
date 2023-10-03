#!/bin/bash

# Detect the operating system
OS="$(uname)"

# Activate virtual environment
if [[ "$OS" == "Linux" ]] || [[ "$OS" == "Darwin" ]]; then
    source venv/bin/activate
elif [[ "$OS" == MINGW64_NT-10.0* ]] || [[ "$OS" == CYGWIN_NT-10.0* ]] || [[ "$OS" == MSYS_NT-10.0* ]]; then
    source venv/Scripts/activate
else
    echo "OS not recognized: $OS"
    exit 1
fi

if ! python -c "import selenium" &> /dev/null; then
    # Ensure pip within the virtual environment is used
  PIP_PATH="$(which pip)"
  if [[ -f "$PIP_PATH" ]]; then
      $PIP_PATH install -r requirements.txt
  else
      echo "pip not found in virtual environment."
      exit 1
  fi
fi

# Navigate to src directory and run main Python script
cd src || exit 1

echo "Running main.py"

python main.py

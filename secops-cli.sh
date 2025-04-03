#!/bin/bash
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Add the src directory to PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Check if .env file exists in the current directory
if [ -f "$SCRIPT_DIR/.env" ]; then
    DOTENV_ARG="--dotenv=$SCRIPT_DIR/.env"
    echo "Using .env file found in $SCRIPT_DIR"
else
    DOTENV_ARG=""
fi

# Run the CLI module directly with the dotenv argument if available
python3 -c "from secops.cli import cli; cli(obj={})" $DOTENV_ARG "$@"

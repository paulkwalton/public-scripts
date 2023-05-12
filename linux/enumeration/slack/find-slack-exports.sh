#!/bin/bash

# Start from root directory
dir="/"

# Define color codes
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Starting to search from the root directory: $dir"

# Find 'exported_data' directories under 'Slack'
echo "Looking for directories named 'exported_data' under any 'Slack' directory..."

find "$dir" -type d -name 'Slack' -exec find {} -type d -name 'exported_data' \; 2>/dev/null | while read dir
do
  echo "Examining files in directory: $dir"
  grep -r -i --color=never 'password' "$dir" 2>/dev/null | while read line
  do
    echo -e "${RED}Potential password found:${NC} $line"
  done
done

echo "Search completed."

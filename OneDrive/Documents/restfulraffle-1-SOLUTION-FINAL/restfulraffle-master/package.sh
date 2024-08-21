#!/bin/bash

PROJECT_DIR="restfulraffle-master"
OUTPUT_ZIP="restfulraffle.zip"

# Change to the project directory
cd "$PROJECT_DIR"

# Remove any existing zip file
rm -f "../$OUTPUT_ZIP"

# Create the zip file, excluding the raffleEnv directory
zip -r "../$OUTPUT_ZIP" . -x "raffleEnv/*"

echo "Project packaged successfully: ../$OUTPUT_ZIP"

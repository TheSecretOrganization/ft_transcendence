#!/bin/sh

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DATA_DIR=$SCRIPT_DIR/../data
STATIC_DIR=$SCRIPT_DIR/../django/src/static
MEDIA_DIR=$SCRIPT_DIR/../django/src/media

echo "Creating .gitkeep in data folder"
touch $DATA_DIR/.gitkeep

echo "Creating .gitkeep in static folder"
touch $STATIC_DIR/.gitkeep

echo "Creating .gitkeep in media folder"
touch $MEDIA_DIR/.gitkeep

echo ".gitkeep files succesfully created"

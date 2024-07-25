#!/bin/sh

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DATA_DIR=$SCRIPT_DIR/../data
STATIC_DIR=$SCRIPT_DIR/../django/src/static
MEDIA_DIR=$SCRIPT_DIR/../django/src/media
RESET_GITKEEP=$SCRIPT_DIR/reset_gitkeep.sh

echo "Removing database..."
rm -rf $DATA_DIR/*

echo "Removing static files..."
rm -rf $STATIC_DIR/*

echo "Removing media files..."
rm -rf $MEDIA_DIR/*

echo "Temporary files succesfuly deleted"

sh $RESET_GITKEEP

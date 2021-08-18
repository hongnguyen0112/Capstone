#!/bin/sh

# Abort on any error (including if wait-for-it fails).
set -e

# Wait for the backend to be up, if we know where it is.
if [ -n "$HOST" ]; then
  ./wait-for-it.sh "$HOST:${PORT:-1729}" 
fi

# Run the main container command.
exec "$@"
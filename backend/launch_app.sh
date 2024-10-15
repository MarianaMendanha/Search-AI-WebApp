#!/bin/bash

echo "Running index_server..."
cd app || { echo "Failed to change directory to app"; exit 1; }
python ./index_server.py & echo "index_server running..."
cd ..

echo "Sleeping for 10 seconds..."
sleep 10

echo "Running Flask server..."
python ./run.py
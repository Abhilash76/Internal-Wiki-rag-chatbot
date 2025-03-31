#!/bin/sh

# Start Ollama server in the background
ollama serve &

echo "Waiting for Ollama server to be active..."
while [ "$(ollama list | grep 'NAME')" == "" ]; do
  sleep 1
done

echo "Start pulling the llama3.1 model..."
ollama pull llama3.1

# Keep the script running and not exit
wait

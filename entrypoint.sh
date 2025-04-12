#!/bin/bash

# Load environment variables
source .env

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

# Retrieve the model defined in the .env file (default to tinyllama if not set)
echo "🔴 Retrieving model: $GRANITE_OLLAMA_LLM..."
ollama pull "$GRANITE_OLLAMA_LLM"
echo "🔴 Retrieving model: $LLAMA_OLLAMA_LLM..."
ollama pull "$LLAMA_OLLAMA_LLM"
echo "🟢 Done!"

# Wait for Ollama process to finish.
wait $pid

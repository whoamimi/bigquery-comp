#!/bin/bash

/bin/ollama serve &

pid=$!

sleep 5

echo "Pulling bartowski's Llama3.2 GGUF model"
ollama run hf.co/bartowski/Llama-3.2-3B-Instruct-GGUF:Q5_K_S

wait $pid
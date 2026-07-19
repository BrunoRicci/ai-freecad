#!/usr/bin/env bash
set -euo pipefail

OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:7b}"
OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11434}"

echo "==> Setting up Ollama + ${OLLAMA_MODEL}..."

if command -v ollama >/dev/null 2>&1; then
    echo "==> Ollama already installed, skipping install."
else
    echo "==> Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo "==> Starting Ollama server in the background..."
export OLLAMA_HOST
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!

echo "==> Waiting for Ollama server to become ready..."
for _ in $(seq 1 30); do
    if curl -fsS "http://${OLLAMA_HOST}/api/version" > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

if ! curl -fsS "http://${OLLAMA_HOST}/api/version" > /dev/null 2>&1; then
    echo "ERROR: Ollama server did not become ready. Check /tmp/ollama.log"
    exit 1
fi

echo "==> Pulling model: ${OLLAMA_MODEL} (this may take a while on first run)..."
ollama pull "${OLLAMA_MODEL}"

echo "==> Stopping temporary Ollama server (PID ${OLLAMA_PID})..."
kill "${OLLAMA_PID}" 2>/dev/null || true
wait "${OLLAMA_PID}" 2>/dev/null || true

echo ""
echo "=========================================="
echo " Ollama setup complete."
echo " Model cached: ${OLLAMA_MODEL}"
echo " Start the server with: ollama serve &"
echo " Chat with:              ollama run ${OLLAMA_MODEL}"
echo "=========================================="

# Local AI (Ollama + Qwen)

This Codespace installs [Ollama](https://ollama.com) and pulls a local
[Qwen](https://ollama.com/library/qwen2.5) model automatically, so the
FreeCAD tooling in this repo can eventually be driven by a local LLM with
no external API calls or keys required.

Setup is wired into `.devcontainer/devcontainer.json` via
`postCreateCommand`, which runs `.devcontainer/setup.sh`. That script now
also runs `ollama/install_ollama.sh`.

## What gets installed

- The Ollama server/CLI, via the official install script.
- The model tagged by `$OLLAMA_MODEL` (default: `qwen2.5:7b`), pulled
  once and cached in `~/.ollama` so rebuilds don't re-download it.

## Configuration

Set these in `.devcontainer/devcontainer.json` under `remoteEnv`, or
export them before opening a Codespace:

| Variable       | Default       | Purpose                                   |
|----------------|---------------|--------------------------------------------|
| `OLLAMA_MODEL` | `qwen2.5:7b`  | Model tag to pull, e.g. `qwen2.5:1.5b` for a smaller footprint |
| `OLLAMA_HOST`  | `127.0.0.1:11434` | Address the Ollama server listens/binds on |

If the Codespace has less than ~8GB RAM, use a smaller tag such as
`qwen2.5:1.5b` or `qwen2.5:3b`.

## Usage

Start the server (the devcontainer does not run it in the background by
default):

```bash
ollama serve &
```

Then either chat directly:

```bash
ollama run qwen2.5:7b
```

Or call the local HTTP API from Python:

```python
import requests

resp = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={"model": "qwen2.5:7b", "prompt": "Say hello.", "stream": False},
)
print(resp.json()["response"])
```

## Manual re-run

```bash
bash ollama/install_ollama.sh
```

This is safe to re-run — it skips the install if `ollama` is already on
`PATH`, and `ollama pull` is a no-op if the model is already present.

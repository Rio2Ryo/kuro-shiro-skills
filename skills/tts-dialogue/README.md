# TTS Dialogue Generator

Generate conversational TTS audio files from a YAML script using OpenAI API.

## Requirements
- Python 3.9+
- OpenAI API Key (`OPENAI_API_KEY` env var)
- Libraries: `openai`, `pyyaml`

## Installation
```bash
pip install openai pyyaml
```

## Usage
1. Prepare your script in YAML format (see example).
2. Edit `generate.py` to set `YAML_PATH` and `OUTPUT_DIR`.
3. Run:
```bash
python generate.py
```

## YAML Format
```yaml
- slide: 1
  lines:
    - speaker: kuro
      text: "Hello!"
    - speaker: shiro
      text: "Hi there!"
```

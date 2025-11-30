# Gemma3 Agent

A Python project for creating AI agents using Gemma.

## Prerequisites

- Python 3.12 or higher

## Virtual Environment Setup

### Activating the Virtual Environment

**macOS/Linux:**
```bash
source gemma-env/bin/activate
```

**Windows:**
```bash
gemma-env\Scripts\activate
```

### Installing Dependencies

After activating the virtual environment, install the required packages:
```bash
pip install -r requirements.txt
```

### Deactivating the Virtual Environment

When you're done working, deactivate the virtual environment:
```bash
deactivate
```

## Commands for LM Studio server

### Get the model

```bash
curl -X GET http://192.168.0.204:1234/v1/models
```

### For direct text completion (non-chat format), use:

```bash
curl http://localhost:1234/api/v0/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/gemma-3-1b-it-qat",
    "prompt": "The capital of Canada is",
    "temperature": 0.7,
    "max_tokens": 50,
    "stream": false
  }'
```
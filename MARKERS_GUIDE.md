# Command Execution Markers Guide

## Overview

The CLI client now supports automatic command execution using special markers. However, model compatibility varies.

## Marker Format

### Execute Commands
```
<<<EXECUTE>>>
command_here
<<</EXECUTE>>>
```

### Create Files
```
<<<CREATE_FILE:path/to/file.ext>>>
file content here
<<</CREATE_FILE>>>
```

## How It Works

1. **System Prompt**: When you start a new session, the AI is instructed to use these markers
2. **Auto-Detection**: The client automatically detects these markers in responses
3. **Auto-Execution**: Commands are executed automatically (with confirmation if enabled)
4. **Context Awareness**: Command outputs are fed back to the AI

## Current Status

⚠️ **Model Compatibility Issue**: The `chatgpt-oss` model appears to have its own internal command format and isn't following our marker instructions.

## Alternative Approaches

### Option 1: Use /commands (Works Now)
This method works with ANY model response:

1. Ask the AI: "How do I list all Python files?"
2. AI responds with explanation and code blocks
3. Type: `/commands`
4. Commands from code blocks are extracted and executed

### Option 2: Try Different Model
Some models follow instructions better:
- Try loading a different model in LM Studio
- Models like GPT-4, Claude, or Llama-3 variants typically follow instructions well
- Change model in config: `~/.lmstudio-cli/config.json`

### Option 3: Disable System Prompt
If you prefer the old behavior:
```json
{
  "use_system_prompt": false
}
```

## Examples

### When Markers Work:
```
You: Create a hello world script and run it
# 🚀 Quick Start Guide

## Installation Complete! ✅

Everything is already set up and ready to use.

## Basic Usage

### Start Interactive Chat
```bash
./lm.sh
```

### Send Single Message
```bash
./lm.sh -m "your question here"
```

## Common Commands

### Session Management
```bash
./lm.sh -l                    # List all sessions
./lm.sh -s 20250111_150527    # Resume a session
./lm.sh -d 20250111_150527    # Show session details
./lm.sh --delete SESSION_ID   # Delete a session
```

### Export & Stats
```bash
./lm.sh -e SESSION_ID         # Export session (markdown)
./lm.sh --stats               # Show usage statistics
```

## Interactive Mode Commands

Once inside interactive mode, use these slash commands:

| Command | What it does |
|---------|-------------|
| `/help` | Show all available commands |
| `/commands` | Execute bash commands from last response |
| `/export` | Export current session |
| `/stats` | Show usage statistics |
| `/history` | Show command execution history |
| `/context` | Show conversation summary |
| `/config` | Show current configuration |
| `/clear` | Clear conversation history |
| `/exit` | Exit the program |

## Example Workflow

1. **Start the client:**
   ```bash
   ./lm.sh
   ```

2. **Ask for help with a task:**
   ```
   You: How do I list all files larger than 1MB?
   ```

3. **Execute the suggested command:**
   ```
   /commands
   ```

4. **Export your session:**
   ```
   /export md
   ```

## Configuration

Config file location: `~/.lmstudio-cli/config.json`

Edit to change:
- API endpoint
- Model name
- Temperature
- Streaming behavior
- Command confirmation
- And more...

## Troubleshooting

**Can't connect?**
- Make sure LM Studio is running
- Check that API server is enabled in LM Studio
- Default port is 1234

**Test connection:**
```bash
curl http://localhost:1234/v1/models
```

## Tips

💡 Ask the AI to write bash commands, then use `/commands` to run them safely

💡 Sessions are auto-saved - you can always resume later

💡 Use command confirmation to review before executing

💡 Export sessions to share your problem-solving process

## Quick Test

```bash
./lm.sh -m "what is 2+2?"
```

Should instantly reply with the answer!

---

For full documentation, see [README.md](README.md)

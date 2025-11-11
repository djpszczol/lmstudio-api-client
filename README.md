# 🤖 LM Studio CLI Client

A beautiful, feature-rich command-line interface for interacting with LM Studio's local API server. Chat with your local LLM, execute bash commands, and manage conversation sessions—all with a colorful, intuitive interface.

## ✨ Features

### Core Features
- 💬 **Interactive Chat** - Real-time streaming responses from your local LLM
- 🎨 **Beautiful UI** - Colorful interface with syntax highlighting using Rich library
- 📝 **Session Management** - Automatic saving of conversations with unique session IDs
- 🔄 **Session Resume** - Continue previous conversations with full context
- ⚡ **Command Execution** - Automatically detect and execute bash commands from responses
- 📊 **Usage Statistics** - Track sessions, messages, commands, and tokens

### Advanced Features
- 🔒 **Safety First** - Confirmation prompts before executing commands
- 💾 **Command History** - Track all executed commands per session
- 🔄 **Auto-Retry** - Automatic retry on connection failures (configurable)
- 📤 **Export Sessions** - Export to Markdown, JSON, or plain text
- 🎯 **Context Awareness** - Save command outputs back to conversation context
- 🔍 **Session Search** - List and view detailed session information
- 🗑️ **Session Management** - Delete old sessions to keep things clean
- ⚙️ **Configurable** - Extensive configuration options

### UI Features
- 🎨 Colorful panels and tables
- ✨ Syntax highlighting for code and command output
- 📊 Beautiful status indicators and progress spinners
- 🎭 Role-based message styling (User vs Assistant)
- 📋 Formatted tables for sessions, stats, and history

## 🚀 Installation

1. **Clone or navigate to the directory:**
```bash
cd lmstudio-api-client
```

2. **Install dependencies (already done - using virtual environment):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Run using the wrapper script:**
```bash
./lm.sh
```

4. **Optional: Create an alias (add to your ~/.zshrc or ~/.bashrc):**
```bash
alias lm='/Users/marekratajczak/lmstudio-api-client/lm.sh'
```

Then you can use just `lm` from anywhere!

## 📋 Prerequisites

- Python 3.8+
- LM Studio running locally with a model loaded
- LM Studio API server enabled (default: http://localhost:1234)

## 🎯 Usage

### Basic Usage

Start a new interactive session:
```bash
./lm.sh
```

### Command-Line Options

```bash
# Resume a previous session
./lm.sh -s 20250111_150527

# Send a single message without entering interactive mode
./lm.sh -m "Explain what ls command does"

# List all sessions
./lm.sh -l

# Show detailed session information
./lm.sh -d 20250111_150527

# Export a session
./lm.sh -e 20250111_150527 --format md

# Show usage statistics
./lm.sh --stats

# Delete a session
./lm.sh --delete 20250111_150527

# Custom API endpoint
./lm.sh --api-base http://localhost:8080/v1

# Use different model
./lm.sh --model gpt-4

# Disable streaming (get full response at once)
./lm.sh --no-stream
```

### Interactive Commands

Once in interactive mode, you can use these commands:

| Command | Description |
|---------|-------------|
| `/exit` or `/quit` | Exit the application |
| `/commands` | Extract and execute commands from last response |
| `/export [format]` | Export current session (md, json, txt) |
| `/clear` | Clear conversation history |
| `/config` | Show current configuration |
| `/stats` | Show usage statistics |
| `/help` | Show help message |
| `/history` | Show command execution history |
| `/context` | Show conversation context summary |

## 🎨 Example Workflow

1. **Start the client:**
```bash
./lm.sh
```

2. **Ask the LLM to write commands:**
```
👤 You: Show me all Python files in the current directory

🤖 Assistant: Here's the command to list all Python files:

```bash
find . -name "*.py" -type f
```

💡 Detected 1 command(s)
```

3. **Execute the commands:**
```
Type: /commands

⚠️  Execute Command?
┌─────────────────────────────────────┐
│ find . -name "*.py" -type f         │
└─────────────────────────────────────┘
Continue? [y/N]: y

▶️  Executing: find . -name "*.py" -type f

📤 Output
┌─────────────────────────────────────┐
│ ./lmcli.py                          │
│ ./tests/test_client.py              │
└─────────────────────────────────────┘

✅ Success
```

4. **Export your session:**
```
Type: /export md

✅ Session exported to: ~/.lmstudio-cli/export_20250111_150527.md
```

## ⚙️ Configuration

Configuration is stored in `~/.lmstudio-cli/config.json`. Default settings:

```json
{
  "api_base": "http://localhost:1234/v1",
  "model": "chatgpt-oss",
  "temperature": 0.7,
  "max_tokens": 2000,
  "stream": true,
  "auto_execute": false,
  "confirm_commands": true,
  "syntax_highlighting": true,
  "save_command_output": true,
  "max_retries": 3,
  "theme": "monokai"
}
```

### Configuration Options

- `api_base`: LM Studio API endpoint
- `model`: Model name to use
- `temperature`: Response randomness (0.0 to 1.0)
- `max_tokens`: Maximum response length
- `stream`: Enable streaming responses
- `auto_execute`: Automatically prompt to execute detected commands
- `confirm_commands`: Ask for confirmation before executing commands
- `syntax_highlighting`: Enable syntax highlighting for code
- `save_command_output`: Add command outputs to conversation context
- `max_retries`: Number of retry attempts on connection failure
- `theme`: Syntax highlighting theme

## 📁 File Structure

```
~/.lmstudio-cli/
├── config.json                    # Configuration file
├── stats.json                     # Usage statistics
├── sessions/
│   ├── session_20250111_150527.json
│   ├── session_20250111_160000.json
│   └── ...
└── export_20250111_150527.md     # Exported sessions
```

## 🔧 Advanced Features

### Session Context

The client maintains full conversation context across messages. When you execute commands using `/commands`, the output can be automatically saved back to the context (if `save_command_output` is enabled), allowing the LLM to "see" the results.

### Command Detection

The client automatically detects bash commands in:
- Code blocks marked with bash/sh/shell/zsh
- Lines starting with `$`

### Auto-Retry Logic

If the connection to LM Studio fails, the client will automatically retry up to `max_retries` times with a 1-second delay between attempts.

### Statistics Tracking

Track your usage:
- Total sessions created
- Total messages sent
- Total commands executed
- Total tokens used (if API provides this info)

View with `./lmcli.py --stats` or `/stats` in interactive mode.

## 🎭 Use Cases

1. **Learning & Exploration**
   - Ask the LLM to explain commands
   - Learn new bash techniques
   - Experiment safely with confirmations

2. **Development Assistance**
   - Generate and test scripts
   - Debug issues with real-time feedback
   - Automate repetitive tasks

3. **System Administration**
   - Get command suggestions
   - Execute with safety confirmations
   - Keep audit trail in session history

4. **Documentation**
   - Export sessions as learning materials
   - Share problem-solving approaches
   - Create tutorials from conversations

## 🛡️ Safety Features

- ✅ Command confirmation prompts (can be disabled)
- ✅ 30-second timeout on command execution
- ✅ Command execution history tracking
- ✅ Non-destructive operations by default
- ✅ Full session audit trail

## 🐛 Troubleshooting

**Connection Issues:**
- Ensure LM Studio is running
- Check if API server is enabled in LM Studio
- Verify the port (default: 1234)
- Try: `curl http://localhost:1234/v1/models`

**Commands Not Detected:**
- Ensure commands are in code blocks with bash/sh/shell/zsh markers
- Or prefix with `$` symbol
- Example: `` ```bash\nls -la\n``` ``

**Dependencies:**
```bash
pip install --upgrade requests rich
```

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Suggestions and improvements welcome! This is a personal utility tool designed for local LLM interaction.

## 🙏 Credits

Built with:
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal formatting
- [Requests](https://requests.readthedocs.io/) - HTTP library
- LM Studio - Local LLM server

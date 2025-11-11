# 🚀 START HERE - Quick Guide

## ✅ Everything Works!

The client is fully functional. Here's how to use it:

## Quick Start

```bash
./lm.sh
```

## How It Works

### Ask + Execute Pattern (⭐ RECOMMENDED)

```bash
# 1. Ask the AI
👤 You> list files in this directory

# 2. AI provides command
🤖 Assistant:
```bash
ls -la
```

# 3. Execute it
👤 You> /commands

💡 Found 1 command(s)
[Runs ls -la]
```

That's it! **Two steps: Ask, then `/commands`**

## Console Mode (Direct Shell)

```bash
# Switch to console mode
👤 You> /console

# Now you have direct shell access
💻 ~/project $ ls -la
💻 ~/project $ cd src
💻 ~/project/src $ pwd
💻 ~/project/src $ ./script.sh

# Back to AI
💻 ~/project/src $ /gpt
```

## Key Features

✅ **Ask AI** - Get help with any command  
✅ **/commands** - Execute code from AI response  
✅ **/console** - Direct shell mode  
✅ **Arrow keys** - Command history (↑/↓)  
✅ **CD works** - Directory changes persist  
✅ **Auto-detect** - ./scripts are recognized  

## Common Commands

```
/commands   - Run code from last AI response
/console    - Switch to shell mode
/gpt        - Return to AI mode
/history    - Show command history
/help       - Show all commands
/exit       - Quit (auto-saves)
```

## Examples

### Find Files
```bash
👤 You> find all python files
🤖 Assistant: [provides find command]
👤 You> /commands
[Executes]
```

### Get System Info
```bash
👤 You> show disk usage
🤖 Assistant: [provides df command]
👤 You> /commands
[Shows disk usage]
```

### Quick Commands in Console
```bash
👤 You> /console
💻 $ ls -la
💻 $ grep -r "TODO" .
💻 $ /gpt
```

## Tips

💡 Use `/commands` after every AI response with code  
💡 Use `/console` for multiple quick commands  
💡 Arrow keys work for command history  
💡 CD actually works! (`cd dir` persists)  
💡 Sessions auto-save, resume with `-s SESSION_ID`  

## Troubleshooting

**AI doesn't provide commands?**
- It should! Just ask: "list files" not "how do I list files"
- Or use `/console` for direct access

**Commands not executing?**
- Did you type `/commands`?
- Are you in console mode? (check for 💻 prompt)

## Full Documentation

- **IT_WORKS.md** - Detailed guide
- **README.md** - Complete documentation
- **QUICKSTART.md** - Quick reference

## Bottom Line

**It's simple:**
1. Start: `./lm.sh`
2. Ask AI anything
3. Type `/commands` to execute
4. Or use `/console` for direct shell

Works 100% reliably! 🎉

---

**Try it now:** `./lm.sh`

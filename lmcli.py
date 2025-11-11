#!/usr/bin/env python3
"""
LM Studio CLI Client - Interactive chat with local LLM and command execution
Beautiful, feature-rich interface with colors and formatting
"""

import os
import sys
import json
import subprocess
import requests
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import re
import time

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.text import Text
from rich import box
from rich.style import Style

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML

# Configuration
CONFIG_DIR = Path.home() / ".lmstudio-cli"
SESSIONS_DIR = CONFIG_DIR / "sessions"
CONFIG_FILE = CONFIG_DIR / "config.json"
STATS_FILE = CONFIG_DIR / "stats.json"

DEFAULT_CONFIG = {
    "api_base": "http://localhost:1234/v1",
    "model": "chatgpt-oss",
    "temperature": 0.7,
    "max_tokens": 2000,
    "stream": True,
    "auto_execute": True,
    "confirm_commands": True,
    "syntax_highlighting": True,
    "save_command_output": True,
    "max_retries": 3,
    "theme": "monokai",
    "use_system_prompt": True  # Helps model provide executable commands
}

SYSTEM_PROMPT = """You are a helpful terminal assistant. When users ask you to execute commands or perform actions, provide the commands in code blocks so they can be executed.

IMPORTANT: When users ask you to DO something (list files, find things, run commands), always provide executable commands in code blocks.

Example:
User: "list files in this directory"
You: "Here are the files:
```bash
ls -la
```"

User: "find Python files"
You: "Searching for Python files:
```bash
find . -name '*.py'
```"

Always provide practical, executable commands when users want to DO something, not just explanations."""

console = Console()


class SessionStats:
    """Track usage statistics"""
    def __init__(self):
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        if STATS_FILE.exists():
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        return {
            "total_sessions": 0,
            "total_messages": 0,
            "total_commands_executed": 0,
            "total_tokens": 0
        }
    
    def save(self):
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def increment(self, key: str, amount: int = 1):
        self.stats[key] = self.stats.get(key, 0) + amount
        self.save()


class LMStudioClient:
    def __init__(self, config: Dict, stats: SessionStats):
        self.config = config
        self.api_base = config["api_base"]
        self.model = config["model"]
        self.session_id = None
        self.session_file = None
        self.messages = []
        self.stats = stats
        self.command_history = []
        self.cwd = os.getcwd()  # Track current working directory
        
    def test_connection(self) -> bool:
        """Test connection to LM Studio"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                progress.add_task(description="Testing connection to LM Studio...", total=None)
                response = requests.get(f"{self.api_base}/models", timeout=5)
                response.raise_for_status()
            console.print("✅ [green]Connected to LM Studio successfully![/green]")
            return True
        except Exception as e:
            console.print(f"❌ [red]Failed to connect to LM Studio: {e}[/red]")
            console.print(f"[yellow]Make sure LM Studio is running on {self.api_base}[/yellow]")
            return False
    
    def create_session(self) -> str:
        """Create a new session with unique ID and inject system prompt"""
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = SESSIONS_DIR / f"session_{self.session_id}.json"
        self.messages = []
        self.command_history = []
        
        # Add system prompt if enabled (as user message since some APIs don't support system role)
        if self.config.get("use_system_prompt", True):
            # Training: show it should provide commands in code blocks
            self.messages.append({"role": "user", "content": SYSTEM_PROMPT})
            self.messages.append({"role": "assistant", "content": "Understood! When users want to DO something, I'll provide executable commands in code blocks using ```bash format. Ready to help!"})
            console.print("[dim green]💡 AI ready to provide executable commands[/dim green]")
        
        self._save_session()
        self.stats.increment("total_sessions")
        return self.session_id
    
    def load_session(self, session_id: str) -> bool:
        """Load an existing session"""
        session_file = SESSIONS_DIR / f"session_{session_id}.json"
        if not session_file.exists():
            return False
        
        with open(session_file, 'r') as f:
            data = json.load(f)
            self.session_id = data['session_id']
            self.messages = data['messages']
            self.command_history = data.get('command_history', [])
            self.session_file = session_file
        
        console.print(f"[green]✅ Loaded session with {len(self.messages)} messages[/green]")
        return True
    
    def _save_session(self):
        """Save current session to file"""
        if not self.session_file:
            return
        
        data = {
            "session_id": self.session_id,
            "created_at": self.session_id,
            "last_updated": datetime.now().isoformat(),
            "messages": self.messages,
            "command_history": self.command_history,
            "message_count": len(self.messages)
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def send_message(self, user_message: str, retry: int = 0) -> Optional[str]:
        """Send message to LM Studio API and get response with retry logic"""
        self.messages.append({"role": "user", "content": user_message})
        self.stats.increment("total_messages")
        
        try:
            url = f"{self.api_base}/chat/completions"
            payload = {
                "model": self.model,
                "messages": self.messages,
                "temperature": self.config["temperature"],
                "max_tokens": self.config["max_tokens"],
                "stream": self.config["stream"]
            }
            
            if self.config["stream"]:
                return self._stream_response(url, payload)
            else:
                response = requests.post(url, json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()
                assistant_message = result['choices'][0]['message']['content']
                
                # Track tokens if available
                if 'usage' in result:
                    self.stats.increment("total_tokens", result['usage'].get('total_tokens', 0))
                
                self.messages.append({"role": "assistant", "content": assistant_message})
                self._save_session()
                return assistant_message
                
        except requests.exceptions.RequestException as e:
            if retry < self.config["max_retries"]:
                console.print(f"[yellow]⚠️  Connection error, retrying... ({retry + 1}/{self.config['max_retries']})[/yellow]")
                time.sleep(1)
                return self.send_message(user_message, retry + 1)
            else:
                console.print(f"[red]❌ Error connecting to LM Studio: {e}[/red]")
                self.messages.pop()  # Remove the user message since it failed
                return None
    
    def _stream_response(self, url: str, payload: Dict) -> Optional[str]:
        """Stream response from API with beautiful formatting"""
        try:
            console.print("\n[dim cyan]🤔 Thinking...[/dim cyan]", end="\r")
            response = requests.post(url, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            
            full_response = ""
            console.print("\n[bold cyan]🤖 Assistant:[/bold cyan]")
            console.print()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    console.print(content, end="", markup=False, highlight=False)
                                    full_response += content
                        except json.JSONDecodeError:
                            continue
            
            console.print("\n")
            self.messages.append({"role": "assistant", "content": full_response})
            self._save_session()
            return full_response
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]❌ Error during streaming: {e}[/red]")
            return None
    
    def get_context_summary(self) -> str:
        """Get summary of current conversation context"""
        user_msgs = sum(1 for m in self.messages if m['role'] == 'user')
        assistant_msgs = sum(1 for m in self.messages if m['role'] == 'assistant')
        return f"{user_msgs} user, {assistant_msgs} assistant"


def looks_like_command(text: str) -> bool:
    """Check if input looks like a shell command"""
    # Common command patterns
    if text.startswith(('./', '../', '/', '~')):
        return True
    if text.startswith(('ls', 'cd', 'pwd', 'cat', 'echo', 'grep', 'find', 'mkdir', 'rm', 'cp', 'mv', 'chmod', 'python', 'node', 'npm', 'git')):
        return True
    # Check for pipes, redirects, etc
    if any(op in text for op in ['|', '>', '<', '&&', '||', ';']):
        return True
    return False


def parse_execute_markers(text: str) -> List[str]:
    """Extract commands from <<<EXECUTE>>> markers"""
    commands = []
    # Try with 3 < signs first
    pattern = r'<<<EXECUTE>>>\s*\n?(.*?)\n?<<</EXECUTE>>>'
    matches = re.findall(pattern, text, re.DOTALL)
    for match in matches:
        cmd = match.strip()
        if cmd:
            commands.append(cmd)
    
    # Also try with 2 < signs in case AI makes mistake
    if not commands:
        pattern = r'<<EXECUTE>>\s*\n?(.*?)\n?<</EXECUTE>>'
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            cmd = match.strip()
            if cmd:
                commands.append(cmd)
    
    return commands


def parse_create_file_markers(text: str) -> List[Dict[str, str]]:
    """Extract file creation instructions from <<<CREATE_FILE:path>>> markers"""
    files = []
    # Try with 3 < signs first  
    pattern = r'<<<CREATE_FILE:([^>]+)>>>\s*\n?(.*?)\n?<<</CREATE_FILE>>>'
    matches = re.findall(pattern, text, re.DOTALL)
    for filepath, content in matches:
        files.append({
            'path': filepath.strip(),
            'content': content
        })
    
    # Also try with 2 < signs in case AI makes mistake
    if not files:
        pattern = r'<<CREATE_FILE:([^>]+)>>\s*\n?(.*?)\n?<</CREATE_FILE>>'
        matches = re.findall(pattern, text, re.DOTALL)
        for filepath, content in matches:
            files.append({
                'path': filepath.strip(),
                'content': content
            })
    
    return files


def extract_commands(text: str) -> List[str]:
    """Extract bash commands from text (code blocks or command patterns)"""
    commands = []
    
    # Extract from code blocks WITH language identifier (```bash, ```sh, etc)
    code_blocks = re.findall(r'```(?:bash|sh|shell|zsh)\n(.*?)```', text, re.DOTALL)
    for block in code_blocks:
        # Each line in the block is a potential command
        for cmd in block.strip().split('\n'):
            cmd = cmd.strip()
            if cmd and not cmd.startswith('#'):
                commands.append(cmd)
    
    # Also extract from code blocks WITHOUT language identifier (just ```)
    # But be more conservative - only if it looks like shell commands
    plain_blocks = re.findall(r'```\n(.*?)```', text, re.DOTALL)
    for block in plain_blocks:
        # Check if this looks like shell commands
        lines = block.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Skip if already found or if it's a comment
            if not line or line.startswith('#') or line in commands:
                continue
            # Check if it looks like a command
            if (line.startswith(('./', '../', '/', '~', 'cd', 'ls', 'pwd', 'cat', 'echo', 
                                'grep', 'find', 'mkdir', 'rm', 'cp', 'mv', 'chmod', 
                                'python', 'node', 'npm', 'git', 'curl', 'wget')) or
                any(op in line for op in ['|', '>', '&&', '||'])):
                commands.append(line)
    
    # Extract inline commands (lines starting with $)
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('$ '):
            cmd = line[2:].strip()
            if cmd not in commands:
                commands.append(cmd)
    
    return commands


def create_file(filepath: str, content: str) -> bool:
    """Create a file with given content"""
    try:
        file_path = Path(filepath)
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        console.print(f"\n[bold blue]📝 Creating file:[/bold blue] [cyan]{filepath}[/cyan]")
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        console.print(f"[green]✅ File created successfully: {filepath}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Failed to create file: {e}[/red]")
        return False


def execute_command(command: str, confirm: bool = True, stats: SessionStats = None, cwd: str = None) -> Tuple[bool, str, str, Optional[str]]:
    """Execute a bash command with optional confirmation
    
    Returns: (success, stdout, stderr, new_cwd)
    new_cwd is only set if command was 'cd', otherwise None
    """
    if confirm:
        console.print(Panel(
            f"[yellow]{command}[/yellow]",
            title="[bold red]⚠️  Execute Command?[/bold red]",
            border_style="yellow"
        ))
        if not Confirm.ask("Continue?", default=False):
            console.print("[red]❌ Skipped[/red]")
            return False, "", "", None
    
    # Handle cd command specially
    cmd_parts = command.strip().split()
    if cmd_parts and cmd_parts[0] == 'cd':
        try:
            if len(cmd_parts) == 1:
                # cd with no args goes to home
                target = os.path.expanduser('~')
            else:
                # cd with path
                target = os.path.expanduser(cmd_parts[1])
                # Make it absolute if relative
                if not os.path.isabs(target):
                    target = os.path.join(cwd or os.getcwd(), target)
            
            # Normalize path
            target = os.path.normpath(target)
            
            # Check if directory exists
            if os.path.isdir(target):
                console.print(f"\n[bold green]📁 Changed directory to:[/bold green] [cyan]{target}[/cyan]")
                return True, target, "", target
            else:
                console.print(f"\n[bold red]❌ Directory not found:[/bold red] {target}")
                return False, "", f"cd: no such file or directory: {target}", None
        except Exception as e:
            console.print(f"\n[bold red]❌ Error changing directory:[/bold red] {e}")
            return False, "", str(e), None
    
    try:
        console.print(f"\n[bold green]▶️  Executing:[/bold green] [cyan]{command}[/cyan]")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd  # Run in the tracked working directory
        )
        
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        if stdout:
            console.print(Panel(
                Syntax(stdout, "text", theme="monokai", word_wrap=True),
                title="[bold green]📤 Output[/bold green]",
                border_style="green"
            ))
        
        if stderr:
            console.print(Panel(
                stderr,
                title="[bold yellow]⚠️  Stderr[/bold yellow]",
                border_style="yellow"
            ))
        
        if result.returncode == 0:
            console.print("[bold green]✅ Success[/bold green]")
            if stats:
                stats.increment("total_commands_executed")
            return True, stdout, stderr, None
        else:
            console.print(f"[bold red]❌ Failed with exit code {result.returncode}[/bold red]")
            return False, stdout, stderr, None
            
    except subprocess.TimeoutExpired:
        console.print("[red]❌ Command timed out (30s limit)[/red]")
        return False, "", "Timeout", None
    except Exception as e:
        console.print(f"[red]❌ Error executing command: {e}[/red]")
        return False, "", str(e), None


def list_sessions():
    """List all available sessions with beautiful table"""
    if not SESSIONS_DIR.exists():
        console.print("[yellow]No sessions found.[/yellow]")
        return
    
    sessions = sorted(SESSIONS_DIR.glob("session_*.json"), reverse=True)
    if not sessions:
        console.print("[yellow]No sessions found.[/yellow]")
        return
    
    table = Table(title="📋 Available Sessions", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Session ID", style="cyan", no_wrap=True)
    table.add_column("Messages", justify="right", style="green")
    table.add_column("Commands", justify="right", style="yellow")
    table.add_column("Last Updated", style="blue")
    
    for session_file in sessions[:20]:  # Show last 20
        with open(session_file, 'r') as f:
            data = json.load(f)
            session_id = data['session_id']
            msg_count = len(data['messages'])
            cmd_count = len(data.get('command_history', []))
            last_updated = data.get('last_updated', 'Unknown')
            if last_updated != 'Unknown':
                last_updated = datetime.fromisoformat(last_updated).strftime("%Y-%m-%d %H:%M")
            table.add_row(session_id, str(msg_count), str(cmd_count), last_updated)
    
    console.print(table)


def show_session_detail(session_id: str):
    """Show detailed view of a session"""
    session_file = SESSIONS_DIR / f"session_{session_id}.json"
    if not session_file.exists():
        console.print(f"[red]❌ Session {session_id} not found[/red]")
        return
    
    with open(session_file, 'r') as f:
        data = json.load(f)
    
    console.print(Panel(
        f"[cyan]Session ID:[/cyan] {data['session_id']}\n"
        f"[cyan]Created:[/cyan] {data['created_at']}\n"
        f"[cyan]Last Updated:[/cyan] {data.get('last_updated', 'Unknown')}\n"
        f"[cyan]Messages:[/cyan] {len(data['messages'])}\n"
        f"[cyan]Commands Executed:[/cyan] {len(data.get('command_history', []))}",
        title="[bold]Session Details[/bold]",
        border_style="cyan"
    ))
    
    if Confirm.ask("Show full conversation?", default=False):
        for i, msg in enumerate(data['messages'], 1):
            role_emoji = "👤" if msg['role'] == 'user' else "🤖"
            role_color = "green" if msg['role'] == 'user' else "cyan"
            console.print(Panel(
                msg['content'],
                title=f"[bold {role_color}]{role_emoji} {msg['role'].title()} (Message {i})[/bold {role_color}]",
                border_style=role_color
            ))


def export_session(session_id: str, format: str = "md"):
    """Export session to file"""
    session_file = SESSIONS_DIR / f"session_{session_id}.json"
    if not session_file.exists():
        console.print(f"[red]❌ Session {session_id} not found[/red]")
        return
    
    with open(session_file, 'r') as f:
        data = json.load(f)
    
    export_file = CONFIG_DIR / f"export_{session_id}.{format}"
    
    with open(export_file, 'w') as f:
        if format == "md":
            f.write(f"# 🤖 LM Studio Session {session_id}\n\n")
            f.write(f"**Created:** {data['session_id']}\n\n")
            f.write(f"**Last Updated:** {data.get('last_updated', 'Unknown')}\n\n")
            f.write(f"**Messages:** {len(data['messages'])}\n\n")
            f.write("---\n\n")
            
            for i, msg in enumerate(data['messages'], 1):
                role = "👤 User" if msg['role'] == 'user' else "🤖 Assistant"
                f.write(f"## {role} (Message {i})\n\n{msg['content']}\n\n")
        elif format == "json":
            json.dump(data, f, indent=2)
        else:  # txt
            for msg in data['messages']:
                role = msg['role'].upper()
                f.write(f"{role}:\n{msg['content']}\n\n{'='*80}\n\n")
    
    console.print(f"[green]✅ Session exported to: {export_file}[/green]")


def delete_session(session_id: str):
    """Delete a session"""
    session_file = SESSIONS_DIR / f"session_{session_id}.json"
    if not session_file.exists():
        console.print(f"[red]❌ Session {session_id} not found[/red]")
        return
    
    if Confirm.ask(f"[red]Delete session {session_id}?[/red]", default=False):
        session_file.unlink()
        console.print(f"[green]✅ Session {session_id} deleted[/green]")


def show_stats(stats: SessionStats):
    """Display usage statistics"""
    table = Table(title="📊 Usage Statistics", box=box.DOUBLE, show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")
    
    for key, value in stats.stats.items():
        metric_name = key.replace('_', ' ').title()
        table.add_row(metric_name, str(value))
    
    console.print(table)


def show_config(config: Dict):
    """Display current configuration"""
    table = Table(title="⚙️  Configuration", box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Setting", style="yellow")
    table.add_column("Value", style="green")
    
    for key, value in config.items():
        table.add_row(key, str(value))
    
    console.print(table)


def show_help():
    """Display help information"""
    help_text = """
[bold cyan]Available Commands:[/bold cyan]

[yellow]/console[/yellow]           - Switch to console mode (direct command execution)
[yellow]/gpt[/yellow]               - Switch back to AI mode
[yellow]/exit[/yellow] or [yellow]/quit[/yellow]     - Exit the application
[yellow]/commands[/yellow]          - Execute commands from last response
[yellow]/export[/yellow] [format]   - Export session (md, json, txt)
[yellow]/clear[/yellow]             - Clear conversation history
[yellow]/config[/yellow]            - Show current configuration
[yellow]/stats[/yellow]             - Show usage statistics
[yellow]/help[/yellow]              - Show this help message
[yellow]/history[/yellow]           - Show command execution history
[yellow]/context[/yellow]           - Show conversation context summary

[bold cyan]Modes:[/bold cyan]
• [bold green]AI Mode[/bold green] - Chat with the AI, auto-detects commands
• [bold yellow]Console Mode[/bold yellow] - Direct bash execution (no AI)

[bold cyan]Tips:[/bold cyan]
• Use ↑/↓ arrow keys to navigate command history
• Commands like ./script.sh are auto-detected in AI mode
• Console mode runs commands instantly (no confirmation)
• Sessions are automatically saved
• Use Ctrl+C to cancel current input
"""
    console.print(Panel(help_text, title="[bold]Help[/bold]", border_style="cyan"))


def interactive_mode(client: LMStudioClient, config: Dict, stats: SessionStats):
    """Run interactive chat mode with beautiful interface"""
    
    # Setup prompt session with history
    history = InMemoryHistory()
    session = PromptSession(history=history)
    
    # Track console mode
    console_mode = False
    
    # Show welcome banner
    console.print(Panel.fit(
        "[bold cyan]🚀 LM Studio CLI Client[/bold cyan]\n"
        f"[green]Session:[/green] {client.session_id}\n"
        f"[green]Model:[/green] {config['model']}\n"
        f"[yellow]Type /help for commands | Ctrl+E for console mode[/yellow]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    
    while True:
        try:
            # Set prompt based on mode
            if console_mode:
                # Show current directory in console mode
                cwd_short = client.cwd.replace(str(Path.home()), '~')
                prompt_text = HTML(f'<ansigreen><b>💻</b></ansigreen> <ansicyan>{cwd_short}</ansicyan> <ansigreen><b>$</b></ansigreen> ')
            else:
                prompt_text = HTML('<ansigreen><b>👤 You></b></ansigreen> ')
            
            # Get input with arrow key history support
            try:
                user_input = session.prompt(prompt_text).strip()
            except KeyboardInterrupt:
                console.print("\n[yellow]Use /exit to quit or Ctrl+E to toggle console mode[/yellow]")
                continue
            
            if not user_input:
                continue
            
            # Toggle console mode with /console or /gpt
            if user_input == "/console":
                console_mode = True
                console.print(Panel(
                    "[bold yellow]💻 CONSOLE MODE ACTIVE[/bold yellow]\n"
                    "Commands are executed directly in shell\n"
                    "Type [cyan]/gpt[/cyan] to return to AI mode",
                    border_style="yellow"
                ))
                continue
            elif user_input == "/gpt":
                console_mode = False
                console.print(Panel(
                    "[bold cyan]🤖 AI MODE ACTIVE[/bold cyan]\n"
                    "Back to conversational AI\n"
                    "Type [yellow]/console[/yellow] to return to console mode",
                    border_style="cyan"
                ))
                continue
            
            # Handle special commands
            if user_input in ["/exit", "/quit"]:
                console.print("[cyan]👋 Goodbye! Session saved.[/cyan]")
                break
                
            elif user_input == "/clear":
                if Confirm.ask("[yellow]Clear conversation history?[/yellow]", default=False):
                    client.messages = []
                    client._save_session()
                    console.print("[green]✅ Conversation cleared[/green]")
                continue
                
            elif user_input.startswith("/export"):
                parts = user_input.split()
                format = parts[1] if len(parts) > 1 else "md"
                export_session(client.session_id, format)
                continue
                
            elif user_input == "/config":
                show_config(config)
                continue
                
            elif user_input == "/stats":
                show_stats(stats)
                continue
                
            elif user_input == "/help":
                show_help()
                continue
                
            elif user_input == "/context":
                summary = client.get_context_summary()
                console.print(f"[cyan]📊 Context: {summary} messages[/cyan]")
                continue
                
            elif user_input == "/history":
                if client.command_history:
                    table = Table(title="Command History", box=box.ROUNDED)
                    table.add_column("#", style="cyan")
                    table.add_column("Command", style="yellow")
                    table.add_column("Status", style="green")
                    for i, cmd in enumerate(client.command_history, 1):
                        table.add_row(str(i), cmd['command'], cmd['status'])
                    console.print(table)
                else:
                    console.print("[yellow]No command history[/yellow]")
                continue
                
            elif user_input == "/commands":
                if client.messages and client.messages[-1]['role'] == 'assistant':
                    last_response = client.messages[-1]['content']
                    commands = extract_commands(last_response)
                    if commands:
                        console.print(f"[cyan]💡 Found {len(commands)} command(s)[/cyan]")
                        for cmd in commands:
                            success, stdout, stderr, new_cwd = execute_command(
                                cmd, 
                                confirm=config["confirm_commands"],
                                stats=stats,
                                cwd=client.cwd
                            )
                            if new_cwd:
                                client.cwd = new_cwd
                            client.command_history.append({
                                "command": cmd,
                                "status": "✅" if success else "❌",
                                "timestamp": datetime.now().isoformat()
                            })
                            if config["save_command_output"] and success:
                                # Add command output to conversation context
                                context_msg = f"Command executed: `{cmd}`\nOutput:\n```\n{stdout}\n```"
                                client.messages.append({"role": "system", "content": context_msg})
                        client._save_session()
                    else:
                        console.print("[yellow]No commands found in last response[/yellow]")
                else:
                    console.print("[yellow]No assistant response to extract commands from[/yellow]")
                continue
            
            # CONSOLE MODE: Execute commands directly
            if console_mode:
                success, stdout, stderr, new_cwd = execute_command(
                    user_input,
                    confirm=False,  # No confirmation in console mode
                    stats=stats,
                    cwd=client.cwd
                )
                if new_cwd:
                    client.cwd = new_cwd
                client.command_history.append({
                    "command": user_input,
                    "status": "✅" if success else "❌",
                    "timestamp": datetime.now().isoformat()
                })
                client._save_session()
                continue
            
            # GPT MODE: Check if input looks like a command
            if looks_like_command(user_input):
                console.print("[yellow]🤔 This looks like a command. Execute it?[/yellow]")
                if Confirm.ask("Run directly?", default=True):
                    success, stdout, stderr, new_cwd = execute_command(
                        user_input,
                        confirm=False,
                        stats=stats,
                        cwd=client.cwd
                    )
                    if new_cwd:
                        client.cwd = new_cwd
                    client.command_history.append({
                        "command": user_input,
                        "status": "✅" if success else "❌",
                        "timestamp": datetime.now().isoformat()
                    })
                    client._save_session()
                    continue
            
            # Send message to LLM
            if config["stream"]:
                # Don't use status spinner with streaming as it clears the output
                response = client.send_message(user_input)
            else:
                with console.status("[bold cyan]🤔 Thinking...", spinner="dots"):
                    response = client.send_message(user_input)
            
            if response is None:
                continue
            
            # Auto-detect and execute markers (<<<EXECUTE>>> and <<<CREATE_FILE>>>)
            files_to_create = parse_create_file_markers(response)
            commands_to_execute = parse_execute_markers(response)
            
            # Create files first
            if files_to_create:
                console.print(f"\n[bold blue]📝 Detected {len(files_to_create)} file(s) to create[/bold blue]")
                for file_info in files_to_create:
                    if create_file(file_info['path'], file_info['content']):
                        client.command_history.append({
                            "command": f"CREATE: {file_info['path']}",
                            "status": "✅",
                            "timestamp": datetime.now().isoformat()
                        })
            
            # Execute commands
            if commands_to_execute:
                console.print(f"\n[bold green]⚡ Detected {len(commands_to_execute)} command(s) to execute[/bold green]")
                for cmd in commands_to_execute:
                    success, stdout, stderr, new_cwd = execute_command(
                        cmd, 
                        confirm=config["confirm_commands"],
                        stats=stats,
                        cwd=client.cwd
                    )
                    if new_cwd:
                        client.cwd = new_cwd
                    client.command_history.append({
                        "command": cmd,
                        "status": "✅" if success else "❌",
                        "timestamp": datetime.now().isoformat()
                    })
                    if config["save_command_output"] and success:
                        # Add command output to conversation context
                        context_msg = f"Command executed successfully: `{cmd}`\nOutput:\n```\n{stdout}\n```"
                        client.messages.append({"role": "system", "content": context_msg})
                client._save_session()
                        
        except KeyboardInterrupt:
            console.print("\n\n[cyan]👋 Goodbye! Session saved.[/cyan]")
            break
        except EOFError:
            break
        except Exception as e:
            console.print(f"[red]❌ Unexpected error: {e}[/red]")


def main():
    parser = argparse.ArgumentParser(
        description="🤖 LM Studio CLI Client - Beautiful, feature-rich interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-s', '--session', help="Resume session by ID")
    parser.add_argument('-l', '--list', action='store_true', help="List all sessions")
    parser.add_argument('-d', '--detail', help="Show session details by ID")
    parser.add_argument('-e', '--export', help="Export session by ID")
    parser.add_argument('--delete', help="Delete session by ID")
    parser.add_argument('-m', '--message', help="Send single message and exit")
    parser.add_argument('--no-stream', action='store_true', help="Disable streaming")
    parser.add_argument('--api-base', help="API base URL")
    parser.add_argument('--model', help="Model name")
    parser.add_argument('--stats', action='store_true', help="Show usage statistics")
    parser.add_argument('--format', default='md', choices=['md', 'json', 'txt'], help="Export format")
    
    args = parser.parse_args()
    
    # Setup directories
    CONFIG_DIR.mkdir(exist_ok=True)
    SESSIONS_DIR.mkdir(exist_ok=True)
    
    # Initialize stats
    stats = SessionStats()
    
    # Load or create config
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = {**DEFAULT_CONFIG, **json.load(f)}
    else:
        config = DEFAULT_CONFIG.copy()
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        console.print(f"[green]✅ Created config file at {CONFIG_FILE}[/green]")
    
    # Override config with args
    if args.api_base:
        config["api_base"] = args.api_base
    if args.model:
        config["model"] = args.model
    if args.no_stream:
        config["stream"] = False
    
    # Handle list command
    if args.list:
        list_sessions()
        return
    
    # Handle detail command
    if args.detail:
        show_session_detail(args.detail)
        return
    
    # Handle stats command
    if args.stats:
        show_stats(stats)
        return
    
    # Handle export command
    if args.export:
        export_session(args.export, args.format)
        return
    
    # Handle delete command
    if args.delete:
        delete_session(args.delete)
        return
    
    # Create client
    client = LMStudioClient(config, stats)
    
    # Test connection
    if not client.test_connection():
        console.print("[yellow]⚠️  Continuing anyway... (connection might work later)[/yellow]")
    
    # Load or create session
    if args.session:
        if not client.load_session(args.session):
            console.print(f"[yellow]⚠️  Session {args.session} not found. Creating new session.[/yellow]")
            client.create_session()
    else:
        client.create_session()
    
    # Single message mode
    if args.message:
        with console.status("[bold cyan]🤔 Thinking...", spinner="dots"):
            response = client.send_message(args.message)
        if response:
            console.print(Panel(
                Markdown(response) if config["syntax_highlighting"] else response,
                title="[bold cyan]🤖 Assistant[/bold cyan]",
                border_style="cyan"
            ))
        return
    
    # Interactive mode
    interactive_mode(client, config, stats)


if __name__ == "__main__":
    main()

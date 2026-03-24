# Whisper Dictate - Global Key Binding

A Python CLI for voice dictation using OpenAI Whisper API with global key binding support on Arch Linux.

## Features

- 🎤 **Toggle Recording**: Single key press to start/stop recording
- 🧠 **AI Transcription**: Uses OpenAI Whisper API for accurate speech-to-text
- 📋 **Clipboard Integration**: Automatically copies transcription to clipboard
- 🔔 **System Notifications**: Visual feedback via notify-send
- ⚡ **Fast Response**: Minimal latency for real-time usage
- 📊 **Persistent History**: SQLite database stores all transcriptions and logs
- 🔍 **CLI Management**: Full command-line interface for managing transcriptions and logs

## Prerequisites

### FFmpeg (Required for MP3 audio support)

FFmpeg is required for MP3 encoding and conversion. Install it via your package manager:

```bash
# Arch Linux
sudo pacman -S ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

## Quick Start

### 1. Install the Package

```bash
# Install in editable mode for development
pip install -e .
```

### 2. Set OpenAI API Key

Create a `.env` file in the project directory or set the environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
# Or add to ~/.bashrc for persistence
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
```

### 3. Add global bind to the CLI

Run the setup script to configure i3:

```bash
# This will modify your i3 config to add the key binding
./setup_i3.sh
```

Or manually add to your i3 config (`~/.config/i3/config`):

```bash
# Bind whisper dictate (using mod+z)
bindsym $mod+z exec whisper-dictate dictate
```

### 4. Test the CLI

```bash
# Check system info
whisper-dictate info

# Run a quick dictation test
whisper-dictate dictate
```

## CLI Usage

The `whisper-dictate` CLI provides multiple subcommands for dictation, logs management, history management, and audio maintenance.

### Global Options

| Option | Description |
|--------|-------------|
| `--log-level LEVEL` | Set logging level (DEBUG, INFO, WARNING, ERROR). Default: INFO |

### Main Commands

#### Dictation

```bash
whisper-dictate dictate [--duration SECONDS]
```

Record audio and transcribe it to text.

**Options:**
- `--duration SECONDS` - Optional recording duration (default: unlimited, stop with Ctrl+C)

**Example:**
```bash
# Record until Ctrl+C
whisper-dictate dictate

# Record for 30 seconds
whisper-dictate dictate --duration 30

# With debug logging
whisper-dictate --log-level DEBUG dictate
```

#### System Information

```bash
whisper-dictate info
```

Display system information including audio devices, clipboard tools, and configuration.

**Example:**
```bash
whisper-dictate info
# Output:
# 🔍 System Information:
# ========================================
# 
# 🎤 Audio Devices:
#   • Built-in Microphone
#   • USB Microphone
# 
# 📋 Clipboard Tools:
#   • xclip
# 
# ⚙️  Configuration:
#   • model: base
#   • language: auto
# 
# 📊 Logging:
#   • Log file: /home/user/.local/share/whisper-dictate/whisper-dictate.log
#   • View logs: tail -f /home/user/.local/share/whisper-dictate/whisper-dictate.log
```

---

## Logs Management

The CLI provides comprehensive log management with database-backed logging and configurable retention.

### List Logs

```bash
whisper-dictate logs list [OPTIONS]
```

Query application logs with filters.

**Options:**
- `--level LEVEL` - Filter by log level (DEBUG, INFO, WARNING, ERROR)
- `--source SOURCE` - Filter by source module (e.g., `whisper_dictate.audio`)
- `--from-time TIME` - Filter from timestamp (ISO format: YYYY-MM-DD HH:MM:SS)
- `--to-time TIME` - Filter to timestamp (ISO format: YYYY-MM-DD HH:MM:SS)
- `--limit N` - Maximum number of logs to display (default: 100)

**Examples:**
```bash
# List recent logs
whisper-dictate logs list

# Show only errors
whisper-dictate logs list --level ERROR

# Filter by source module
whisper-dictate logs list --source whisper_dictate.audio --limit 50

# Filter by date range
whisper-dictate logs list --from-time "2024-01-01" --to-time "2024-01-31"
```

### Export Logs

```bash
whisper-dictate logs export FILENAME [OPTIONS]
```

Export logs to a file in text or JSON format.

**Options:**
- `--format FORMAT` - Export format: text or json (default: text)
- All filter options from `logs list` are available

**Examples:**
```bash
# Export to text file
whisper-dictate logs export error_logs.txt --level ERROR

# Export to JSON
whisper-dictate logs export logs.json --format json
```

### Cleanup Logs

```bash
whisper-dictate logs cleanup [OPTIONS]
```

Clean up old logs based on retention policy.

**Options:**
- `--days N` - Delete logs older than N days (default: use configured retention)

**Examples:**
```bash
# Use default retention (configured in database)
whisper-dictate logs cleanup

# Delete logs older than 7 days
whisper-dictate logs cleanup --days 7
```

---

## History Management

Search, view, and manage your transcription history stored in the SQLite database.

### List History

```bash
whisper-dictate history list [OPTIONS]
```

List recent transcriptions with pagination.

**Options:**
- `--limit N` - Maximum number to display (default: 20)
- `--date YYYY-MM-DD` - Filter by specific date

**Examples:**
```bash
# List recent transcriptions
whisper-dictate history list

# Show last 10
whisper-dictate history list --limit 10

# Filter by date
whisper-dictate history list --date 2024-03-15
```

### Show Transcription Details

```bash
whisper-dictate history show ID [OPTIONS]
```

Show full details of a specific transcription.

**Options:**
- `--audio` - Show the audio file path

**Examples:**
```bash
# Show transcription details
whisper-dictate history show 42

# Include audio file path
whisper-dictate history show 42 --audio
```

### Search Transcriptions

```bash
whisper-dictate history search QUERY [OPTIONS]
```

Search transcriptions by text (case-insensitive).

**Options:**
- `--limit N` - Maximum number of results (default: 20)

**Examples:**
```bash
# Search for "meeting"
whisper-dictate history search "meeting"

# Search with more results
whisper-dictate history search "project" --limit 50
```

### Delete Transcription

```bash
whisper-dictate history delete ID [OPTIONS]
```

Delete a transcription and its associated audio file.

**Options:**
- `--yes` - Skip confirmation prompt

**Examples:**
```bash
# Delete with confirmation
whisper-dictate history delete 42

# Delete without confirmation
whisper-dictate history delete 42 --yes
```

### Update Transcription

```bash
whisper-dictate history update ID [OPTIONS]
```

Update a transcription's text and optionally language.

**Options:**
- `--text "NEW TEXT"` - New transcript text (required)
- `--language CODE` - New language code (optional, e.g., "en", "es")

**Examples:**
```bash
# Update text only
whisper-dictate history update 123 --text "corrected transcription"

# Update text and language
whisper-dictate history update 123 --text "new text" --language en
```

---

## Audio Management

### Cleanup Orphaned Files

```bash
whisper-dictate audio cleanup [OPTIONS]
```

Clean up orphaned audio files not referenced in the database.

**Options:**
- `--dry-run` - Show what would be deleted without actually deleting (default: True)
- `--confirm` - Actually delete the orphaned files (default: False)

**Examples:**
```bash
# Preview what would be deleted (default)
whisper-dictate audio cleanup

# Actually delete orphaned files
whisper-dictate audio cleanup --confirm
```

---

## Migration

### Migrate Legacy State Files

```bash
whisper-dictate migrate [OPTIONS]
```

Migrate legacy state files to the database.

**Options:**
- `--force` - Force re-migration even if already completed
- `--status` - Check migration status only

**Examples:**
```bash
# Check migration status
whisper-dictate migrate --status

# Run migration
whisper-dictate migrate

# Force re-migration
whisper-dictate migrate --force
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project directory:

```bash
OPENAI_API_KEY=your-api-key-here
LOG_LEVEL=INFO
```

### Database Configuration

The CLI uses a SQLite database stored at:
```
~/.local/share/whisper-dictate/whisper-dictate.db
```

Configuration options (in `.env`):
- `LOG_RETENTION_DAYS` - Days to keep logs (default: 30)
- `MIN_FREE_SPACE_MB` - Minimum free disk space required for recording (default: 100)

### Audio Settings

The CLI uses sensible defaults:
- Sample rate: 16kHz (optimal for Whisper)
- Channels: 1 (mono)
- Format: 16-bit WAV

---

## Notification Action Buttons

When recording, the notification displays a "Stop Recording" action button. There are two ways to use it:

### Prerequisites

1. **Install dunst and dmenu** (required for action buttons):
   ```bash
   # Arch Linux
   sudo pacman -S dunst dmenu

   # Debian/Ubuntu
   sudo apt-get install dunst dmenu
   ```

2. **Start dunst notification daemon** if not already running:
   ```bash
   dunst &
   ```

### i3 Configuration for Context Menu

To use the notification action button, you need to configure a keybinding for dunst's context menu in your i3 config (`~/.config/i3/config`):

```bash
# Dunst context menu keybinding (required for notification actions)
bindsym Ctrl+Shift+. exec dunstctl context
```

Reload i3 after adding:
```bash
i3-msg reload
```

### How to Use Action Buttons

**Method 1: Click the notification (if supported)**
- Some dunst configurations support clicking action buttons directly on the notification

**Method 2: Use the context menu**
1. While recording, press `Ctrl+Shift+.` to open dunst's context menu
2. Select "Stop Recording" from the menu
3. The recording will stop and transcription will begin

**Note:** The context menu keybinding (`Ctrl+Shift+.`) is configurable in your dunst configuration. Check your dunstrc for the `shortcut` setting under `[global]` or `[keybind]` sections.

---

## Troubleshooting

### Dependencies Missing
```bash
# Install missing Python packages
pip install -e .

# Install system packages
sudo pacman -S python-pip ffmpeg portaudio
```

### No Audio Devices
```bash
# List available audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Clipboard Not Working
```bash
# Install clipboard tools
sudo pacman -S xclip xsel wl-clipboard
```

### Debug Mode
```bash
# Run with debug logging
whisper-dictate --log-level DEBUG dictate
```

### View Application Logs
```bash
# Tail the log file
tail -f ~/.local/share/whisper-dictate/whisper-dictate.log

# Or use the CLI to query logs
whisper-dictate logs list --level DEBUG
```

### Database Issues
```bash
# Check database location
ls -la ~/.local/share/whisper-dictate/

# Check migration status
whisper-dictate migrate --status

# Re-run migration if needed
whisper-dictate migrate --force
```

---

## Key Files

- **`whisper_dictate/`** - Main Python package
  - `cli.py` - Click-based CLI interface
  - `dictation.py` - Core dictation service
  - `database.py` - SQLite database operations
  - `transcription.py` - Whisper API integration
  - `notifications.py` - System notifications
  - `clipboard.py` - Clipboard integration
- **`setup.py`** - Package installation configuration
- **`main.py`** - CLI entry point script
- **`.env`** - Environment configuration

---

## Usage Tips

- **Speak clearly** and at normal pace
- **Use in quiet environment** for best results
- **Test with short recordings** first
- **Check system notifications** for status updates
- **Use `history` commands** to review past transcriptions
- **Use `logs` commands** for debugging issues

The CLI is designed to be fast and responsive, with minimal latency between key press and recording start/stop.
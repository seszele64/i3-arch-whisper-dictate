# Whisper Dictate - Global Key Binding

A Python script for voice dictation using OpenAI Whisper API with global key binding support on Arch Linux.

## Features

- 🎤 **Toggle Recording**: Single key press to start/stop recording
- 🧠 **AI Transcription**: Uses OpenAI Whisper API for accurate speech-to-text
- 📋 **Clipboard Integration**: Automatically copies transcription to clipboard
- 🔔 **System Notifications**: Visual feedback via notify-send
- 🔧 **Global Key Binding**: Works with any window manager
- ⚡ **Fast Response**: Minimal latency for real-time usage

## Quick Start

### 1. Install Dependencies
```bash
# Run the installation script
chmod +x install_global.sh
./install_global.sh
```

### 2. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your-api-key-here"
# Or add to ~/.bashrc for persistence
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
```

### 3. Set Global Key Binding

#### i3 Window Manager
Add to `~/.config/i3/config`:
```bash
bindsym $mod+d exec --no-startup-id whisper-dictate
```

#### KDE Plasma
1. System Settings → Shortcuts → Custom Shortcuts
2. Add Command: `whisper-dictate`
3. Set your preferred key combination

#### GNOME
1. Settings → Keyboard → Custom Shortcuts
2. Add custom shortcut
3. Command: `whisper-dictate`

#### Sway
Add to `~/.config/sway/config`:
```bash
bindsym $mod+d exec whisper-dictate
```

## Usage

### Basic Usage
1. **Press your bound key** to start recording
2. **Speak naturally** - no time limit
3. **Press the same key again** to stop and transcribe
4. **Transcription is automatically copied to clipboard**

### Manual Installation
If you prefer manual installation:

```bash
# Install system dependencies
sudo pacman -S python python-pip ffmpeg portaudio xclip xsel wl-clipboard

# Install Python dependencies
pip install --user -r requirements.txt

# Make script executable
chmod +x toggle_dictate.py

# Create symlink
ln -sf "$(pwd)/toggle_dictate.py" ~/.local/bin/whisper-dictate
```

## Configuration

### Environment Variables
Create a `.env` file in the same directory:
```bash
OPENAI_API_KEY=your-api-key-here
LOG_LEVEL=INFO
COPY_TO_CLIPBOARD=true
```

### Audio Settings
The script uses sensible defaults:
- Sample rate: 16kHz (optimal for Whisper)
- Channels: 1 (mono)
- Format: 16-bit WAV

## Troubleshooting

### Dependencies Missing
```bash
# Install missing Python packages
pip install --user -r requirements.txt

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
LOG_LEVEL=DEBUG python toggle_dictate.py
```

find logs using
```bash
tail -f ~/.local/share/whisper-dictate/whisper-dictate.log
```

## Architecture

The toggle system uses:
- **Global state management** to track recording across invocations
- **Thread-safe audio capture** with proper cleanup
- **System notifications** for user feedback
- **Error handling** for robust operation

## Key Files

- **`toggle_dictate.py`** - Main toggle script for global binding
- **`install_global.sh`** - Automated installation script
- **`whisper_dictate/`** - Core modules (reused from previous implementation)

## Usage Tips

- **Speak clearly** and at normal pace
- **Use in quiet environment** for best results
- **Test with short recordings** first
- **Check system notifications** for status updates
- **Restart window manager** after setting key bindings

The system is designed to be fast and responsive, with minimal latency between key press and recording start/stop.
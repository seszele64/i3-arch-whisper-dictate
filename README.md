# Whisper Dictate

A simple, strongly-typed Python script for voice dictation using OpenAI Whisper API on Arch Linux. Records audio, transcribes it using OpenAI's cloud-based Whisper API, and copies the result to your clipboard.

## Features

- 🎤 **Audio Recording**: Configurable duration and quality
- 🧠 **AI Transcription**: Uses OpenAI Whisper API for accurate speech-to-text
- 📋 **Clipboard Integration**: Automatically copies transcription to clipboard
- 🔧 **Strong Typing**: Full type annotations for better IDE support
- 📝 **Comprehensive Logging**: Detailed logs for debugging
- ⚙️ **Configurable**: Environment-based configuration

## Installation

### System Dependencies (Arch Linux)

```bash
# Install system dependencies
sudo pacman -S python python-pip ffmpeg portaudio

# Install clipboard tools (at least one of these)
sudo pacman -S xclip xsel wl-clipboard
```

### Python Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### Configuration

1. **Get OpenAI API Key**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Set Environment Variable**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
3. **Optional**: Copy `.env.example` to `.env` and customize:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Usage

### Basic Usage

```bash
# Record for default duration (5 seconds)
python -m whisper_dictate dictate

# Record for specific duration
python -m whisper_dictate dictate --duration 10

# Using the main script
python main.py dictate
```

### Commands

- **`dictate`**: Start recording and transcribe
- **`info`**: Display system information and available devices

### Examples

```bash
# Record for 8 seconds
python main.py dictate --duration 8

# Check system information
python main.py info

# Run with debug logging
python main.py --log-level DEBUG dictate
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | **Required** OpenAI API key |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `AUDIO_DURATION` | `5.0` | Default recording duration in seconds |
| `COPY_TO_CLIPBOARD` | `true` | Whether to copy transcription to clipboard |

### Audio Configuration

You can override audio settings by modifying the configuration in code or extending the config system.

## Troubleshooting

### Common Issues

1. **No audio devices found**:
   ```bash
   python main.py info
   ```
   Check if your microphone is connected and recognized.

2. **Clipboard not working**:
   - Ensure `xclip`, `xsel`, or `wl-copy` is installed
   - Run `python main.py info` to see available clipboard tools

3. **OpenAI API errors**:
   - Verify your API key is set correctly
   - Check your OpenAI account has credits
   - Ensure network connectivity

### Debug Mode

Run with debug logging for detailed information:
```bash
python main.py --log-level DEBUG dictate
```

## Architecture

The application follows a clean architecture with clear separation of concerns:

- **`config.py`**: Configuration management with Pydantic models
- **`audio.py`**: Audio recording functionality
- **`transcription.py`**: OpenAI Whisper API integration
- **`clipboard.py`**: Linux clipboard operations
- **`dictation.py`**: Main service orchestration
- **`cli.py`**: Command-line interface

## Development

### Project Structure

```
whisper-dictate/
├── whisper_dictate/
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── audio.py
│   ├── transcription.py
│   ├── clipboard.py
│   ├── dictation.py
│   └── cli.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

### Running Tests

```bash
# Install in development mode
pip install -e .

# Run basic functionality test
python -c "from whisper_dictate.config import load_config; print('Config loaded successfully')"
```

## License

MIT License - feel free to use and modify as needed.
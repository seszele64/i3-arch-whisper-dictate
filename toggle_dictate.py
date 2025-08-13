#!/usr/bin/env python3
"""
Fixed toggle dictation for i3 - proper real-time recording with immediate start/stop.
"""
import os
import sys
import time
import tempfile
import logging
import signal
import subprocess
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from whisper_dictate.config import load_config
from whisper_dictate.transcription import WhisperTranscriber
from whisper_dictate.clipboard import ClipboardManager
from whisper_dictate.notifications import (
    notify_recording_started,
    notify_recording_stopped,
    notify_error,
    notify_stopping_transcription
)

# State and process tracking
STATE_FILE = Path.home() / '.whisper-dictate-state'
PID_FILE = Path.home() / '.whisper-dictate-pid'
AUDIO_FILE = Path.home() / '.whisper-dictate-audio.wav'

def setup_logging():
    """WHY THIS EXISTS: Logging needs to be configured consistently
    across the application for debugging and monitoring.
    
    RESPONSIBILITY: Configure logging with file output to whisper-dictate.log.
    BOUNDARIES:
    - DOES: Set up logging configuration with file output
    - DOES NOT: Handle log rotation or file management
    """
    import os
    from pathlib import Path
    
    # Create log directory
    log_dir = Path.home() / '.local' / 'share' / 'whisper-dictate'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / 'whisper-dictate.log'
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

def is_recording():
    """Check if currently recording."""
    return PID_FILE.exists() and STATE_FILE.exists()

def get_recording_pid():
    """Get the PID of the recording process."""
    try:
        if PID_FILE.exists():
            return int(PID_FILE.read_text().strip())
    except (ValueError, OSError):
        pass
    return None

def start_background_recording(config):
    """Start background recording process using arecord."""
    try:
        # Build the command - use default device
        cmd = [
            'arecord',
            '-f', 'cd',  # CD quality: 16-bit little-endian, 44100Hz, stereo
            '-t', 'wav',
            str(AUDIO_FILE)
        ]
        
        # Start the recording process
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Save PID for later management
        PID_FILE.write_text(str(process.pid))
        STATE_FILE.touch()
        
        logging.info("Recording started")
        notify_recording_started()
        
        return process
        
    except Exception as e:
        logging.error(f"Failed to start recording: {e}")
        notify_error(f"Failed to start recording: {e}")
        return None

def stop_background_recording():
    """Stop background recording and process the audio."""
    try:
        pid = get_recording_pid()
        if pid:
            # Kill the recording process
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.5)  # Give it time to stop
                os.kill(pid, signal.SIGKILL)  # Force kill if needed
            except ProcessLookupError:
                pass  # Process already dead
            
            # Clean up PID file
            if PID_FILE.exists():
                PID_FILE.unlink()
                
        # Clean up state file
        if STATE_FILE.exists():
            STATE_FILE.unlink()
            
        return True
        
    except Exception as e:
        logging.error(f"Error stopping recording: {e}")
        return False

def transcribe_audio(config):
    """Transcribe the recorded audio."""
    try:
        if not AUDIO_FILE.exists():
            logging.error("No audio file found")
            return None
            
        logging.info("Starting transcription")
        transcriber = WhisperTranscriber(config.openai)
        result = transcriber.transcribe_audio(AUDIO_FILE)
        
        # Copy to clipboard
        clipboard = ClipboardManager()
        clipboard.copy_to_clipboard(result.text)
        
        logging.info(f"Transcription completed: {result.text}")
        notify_recording_stopped(result.text)
        
        return result.text
        
    except Exception as e:
        logging.error(f"Transcription error: {e}")
        notify_error(f"Transcription failed: {e}")
        return None
        
    finally:
        # Clean up audio file
        if AUDIO_FILE.exists():
            AUDIO_FILE.unlink()

def main():
    """Main function - real toggle recording."""
    setup_logging()
    
    try:
        config = load_config()
        
        if is_recording():
            logging.info("Stopping recording...")
            notify_stopping_transcription()
            if stop_background_recording():
                transcribe_audio(config)
            else:
                logging.error("Failed to stop recording properly")
        else:
            # Start new recording
            process = start_background_recording(config)
            if process is None:
                logging.error("Failed to start recording")
                sys.exit(1)
                
    except Exception as e:
        logging.error(f"Error: {e}")
        notify_error(str(e))
        # Clean up on error
        stop_background_recording()
        if AUDIO_FILE.exists():
            AUDIO_FILE.unlink()

if __name__ == "__main__":
    main()
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

# State and process tracking
STATE_FILE = Path.home() / '.whisper-dictate-state'
PID_FILE = Path.home() / '.whisper-dictate-pid'
AUDIO_FILE = Path.home() / '.whisper-dictate-audio.wav'

def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

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
        
        print("🎤 Recording started...")
        os.system('notify-send "Dictation" "Recording started... press again to stop"')
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start recording: {e}")
        os.system(f'notify-send "Dictation Error" "Failed to start recording: {e}"')
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
        print(f"❌ Error stopping recording: {e}")
        return False

def transcribe_audio(config):
    """Transcribe the recorded audio."""
    try:
        if not AUDIO_FILE.exists():
            print("❌ No audio file found")
            return None
            
        print("🧠 Transcribing...")
        transcriber = WhisperTranscriber(config.openai)
        result = transcriber.transcribe_audio(AUDIO_FILE)
        
        # Copy to clipboard
        clipboard = ClipboardManager()
        clipboard.copy_to_clipboard(result.text)
        
        print(f"📝 Transcription: {result.text}")
        os.system(f'notify-send "Dictation" "Transcription: {result.text[:50]}..."')
        
        return result.text
        
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        os.system(f'notify-send "Dictation Error" "Transcription failed: {e}"')
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
            print("🛑 Stopping recording...")
            if stop_background_recording():
                transcribe_audio(config)
            else:
                print("❌ Failed to stop recording properly")
        else:
            # Start new recording
            process = start_background_recording(config)
            if process is None:
                print("❌ Failed to start recording")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ Error: {e}")
        os.system(f'notify-send "Dictation Error" "{str(e)}"')
        # Clean up on error
        stop_background_recording()
        if AUDIO_FILE.exists():
            AUDIO_FILE.unlink()

if __name__ == "__main__":
    main()
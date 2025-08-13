#!/usr/bin/env python3
"""
WHY THIS EXISTS: i3 notifications are used throughout the application to provide
user feedback for recording states, transcription results, and error conditions.
Centralizing this prevents inconsistent notification styling and makes it easier
to maintain notification behavior across the application.

RESPONSIBILITY: Provide a clean, type-safe interface for sending desktop notifications
in i3 window manager environments.

BOUNDARIES:
- DOES: Send desktop notifications with configurable urgency, timeout, and content
- DOES NOT: Handle notification history, interactive notifications, or sound alerts
- DEPENDS ON: notify-send command being available in the system
- USED BY: toggle_dictate.py and other modules that need user feedback

🧠 ADHD CONTEXT: Having a single, well-documented function for notifications
prevents the cognitive load of remembering notify-send syntax and parameters.
"""

import subprocess
from typing import Literal, Optional

# Type aliases for notification parameters
UrgencyLevel = Literal["low", "normal", "critical"]
TimeoutMs = int  # Timeout in milliseconds


def send_notification(
    summary: str,
    body: str = "",
    urgency: UrgencyLevel = "normal",
    timeout: TimeoutMs = 5000
) -> bool:
    """
    WHY THIS EXISTS: Provides a consistent way to send desktop notifications
    across the application with proper error handling and type safety.
    
    RESPONSIBILITY: Send a desktop notification using notify-send command.
    
    DOES:
    - Send notifications with configurable urgency and timeout
    - Handle command execution errors gracefully
    - Provide boolean success/failure feedback
    
    DOES NOT:
    - Queue notifications if system is busy
    - Handle notification server unavailability
    - Provide notification history or callbacks
    
    Args:
        summary: The notification title/summary text
        body: Optional detailed message body
        urgency: Notification urgency level ("low", "normal", or "critical")
        timeout: Display duration in milliseconds (0 for persistent)
        
    Returns:
        bool: True if notification was sent successfully, False otherwise
        
    Examples:
        >>> send_notification("Recording Started", "Press again to stop")
        True
        >>> send_notification("Error", "Failed to start recording", "critical", 10000)
        True
    """
    try:
        cmd = [
            "notify-send",
            f"--urgency={urgency}",
            f"--expire-time={timeout}",
            summary,
            body
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        return result.returncode == 0
        
    except FileNotFoundError:
        # notify-send command not found
        return False
    except Exception:
        # Other subprocess errors
        return False


def notify_recording_started() -> bool:
    """
    WHY THIS EXISTS: Standardized notification for when recording begins.
    
    RESPONSIBILITY: Send a consistent "recording started" notification.
    
    Returns:
        bool: True if notification sent successfully
    """
    return send_notification(
        summary="Dictation",
        body="Recording started... press again to stop",
        urgency="normal",
        timeout=3000
    )


def notify_recording_stopped(text_preview: str = "") -> bool:
    """
    WHY THIS EXISTS: Standardized notification for when recording stops.
    
    RESPONSIBILITY: Send a consistent "recording stopped" notification with
    optional transcription preview.
    
    Args:
        text_preview: First part of transcribed text to show
        
    Returns:
        bool: True if notification sent successfully
    """
    body = "Recording stopped and processing..."
    if text_preview:
        if len(text_preview) > 52:
            preview = text_preview[:49] + "..."  # 49 + 3 = 52 total
        else:
            preview = text_preview
        body = f"Transcription: {preview}"
    
    return send_notification(
        summary="Dictation",
        body=body,
        urgency="normal",
        timeout=5000
    )


def notify_error(error_message: str) -> bool:
    """
    WHY THIS EXISTS: Standardized error notifications for consistent user feedback.
    
    RESPONSIBILITY: Send a consistent error notification with the provided message.
    
    Args:
        error_message: The error description to display
        
    Returns:
        bool: True if notification sent successfully
    """
    return send_notification(
        summary="Dictation Error",
        body=error_message,
        urgency="critical",
        timeout=10000
    )


def notify_info(info_message: str) -> bool:
    """
    WHY THIS EXISTS: Standardized info notifications for non-critical feedback.
    
    RESPONSIBILITY: Send a consistent informational notification.
    
    Args:
        info_message: The information message to display
        
    Returns:
        bool: True if notification sent successfully
    """
    return send_notification(
        summary="Dictation",
        body=info_message,
        urgency="low",
        timeout=3000
    )


def notify_stopping_transcription() -> bool:
    """
    WHY THIS EXISTS: Provides immediate user feedback when recording is stopped
    and transcription is about to begin, preventing confusion about whether
    the key press was registered.
    
    RESPONSIBILITY: Send a consistent "stopping recording" notification.
    
    Returns:
        bool: True if notification sent successfully
    """
    return send_notification(
        summary="Dictation",
        body="Stopping recording... processing audio",
        urgency="normal",
        timeout=2000
    )
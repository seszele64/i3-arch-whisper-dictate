# Quickstart: Persistent Notification Feature

**Feature**: Persistent Notification During Recording  
**Date**: 2026-02-15

## Overview

This feature adds persistent notifications to the whisper-dictate recording workflow. When you start recording, a notification stays visible until you stop recording.

## Prerequisites

- Linux with i3 window manager
- dunst notification daemon installed and running
- dunstify command available (install via `dunst` package)
- Fallback: notify-send (libnotify) if dunstify unavailable

## Usage

### Starting Recording

1. Press your configured hotkey to start recording
2. A persistent notification appears: "Recording..."
3. The notification stays visible throughout the recording

### During Recording

- The notification remains visible (never auto-dismisses)
- If real-time transcription is enabled (Issue #2), text updates appear in the notification

### Stopping Recording

1. Press your configured hotkey to stop OR
2. Click the notification and select "Stop Recording" (requires dunst context menu: Ctrl+Shift+.)

The notification closes automatically when recording stops.

## Configuration

No additional configuration required. The feature uses sensible defaults:

- **Timeout**: 0 (persistent - never dismiss)
- **Urgency**: critical (high visibility)
- **Stack tag**: "recording" (ensures single notification)

## Troubleshooting

### Notification doesn't appear

1. Check if dunst is running: `pgrep -f dunst`
2. Start dunst manually: `dunst`
3. Check logs: `tail -f ~/.local/share/whisper-dictate/whisper-dictate.log`

### Fallback mode

If dunstify is not available, the system falls back to notify-send. Notifications will work but may not be persistent.

### Stop action not working

The stop action requires dunst's context menu:
1. Press Ctrl+Shift+. (default dunst shortcut)
2. Click on the recording notification
3. Select "Stop Recording"

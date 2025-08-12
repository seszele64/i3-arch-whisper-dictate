#!/bin/bash
# Setup i3 global key binding for whisper-dictate

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/toggle_dictate.py"
I3_CONFIG="$HOME/.config/i3/config"
BINDING="bindsym \$mod+z exec --no-startup-id python3 $SCRIPT_PATH"

echo "Setting up i3 global key binding for whisper-dictate..."

# Check if i3 config exists
if [ ! -f "$I3_CONFIG" ]; then
    echo "i3 config not found at $I3_CONFIG"
    exit 1
fi

# Check if binding already exists
if grep -q "toggle_dictate.py" "$I3_CONFIG"; then
    echo "Key binding already exists in i3 config"
else
    # Add the key binding
    echo "" >> "$I3_CONFIG"
    echo "# Voice dictation toggle - Super+Z" >> "$I3_CONFIG"
    echo "$BINDING" >> "$I3_CONFIG"
    echo "Added key binding: Super+Z"
fi

# Reload i3
i3-msg reload
echo "i3 configuration reloaded!"
echo "Press Super+Z to test voice dictation"
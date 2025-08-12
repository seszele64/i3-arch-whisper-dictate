```bash
cp run_whisper_dictate.sh ~/.config/scripts/run_whisper_dictate.sh
chmod +x ~/.config/scripts/run_whisper_dictate.sh
```

add to i3wm config

usually at `~/.config/i3/config`

```
# Bind whisper dictate
## Voice dictation toggle - Super+Z
bindsym $mod+z exec ~/.config/scripts/run_whisper_dictate.sh
```

to use modification key + z in this case to run whisper dictation (on/off) switch on mod+z
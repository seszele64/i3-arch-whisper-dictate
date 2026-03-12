## 1. Implement stack tag-based notification functions

- [x] 1.1 Add RECORDING_STACK_TAG constant to notifications.py
- [x] 1.2 Implement notify_recording_start() function using stack tags
      - Uses `-h string:x-dunst-stack-tag:whisper-dictate-recording`
      - Persistent timeout (-t 0) with critical urgency (-u critical)
- [x] 1.3 Implement notify_recording_stop() function using stack tags
      - Uses same stack tag to replace persistent notification
      - 2-second timeout (-t 2000) with normal urgency
- [x] 1.4 Add graceful fallback when dunstify is unavailable in both functions

## 2. Update toggle_dictate.py to use new notification functions

- [x] 2.1 Import notify_recording_start and notify_recording_stop
- [x] 2.2 Replace old notification calls with new stack tag functions
- [x] 2.3 Update recording start path to use notify_recording_start()
- [x] 2.4 Update recording stop path to use notify_recording_stop()

## 3. Testing and Verification

- [x] 3.1 Run existing tests to ensure no regression
- [x] 3.2 Verify stack tag notifications work correctly
- [x] 3.3 Verify notification replacement behavior (stop replaces start)
- [x] 3.4 Verify graceful fallback when dunstify unavailable

## 4. Documentation

- [x] 4.1 Update spec.md with stack tag requirements and scenarios
- [x] 4.2 Update design.md with stack tag technical approach
- [x] 4.3 Update tasks.md to reflect completed work

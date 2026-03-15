---
category: lesson-learned
tags: [pytest, debugging, threading, aiosqlite, testing, testing-infrastructure]
created: 2026-03-15
---

# Pytest Hang Issue - Debugging Session

## What happened
- Pytest would hang indefinitely after tests completed
- Tests passed but process wouldn't exit
- Ctrl+C showed threading._shutdown lock acquisition error

## Initial investigation
- Multiple suspected causes: sounddevice/PortAudio, lazy imports, fixture cleanup
- Multiple attempted fixes that didn't work
- Required deeper architectural analysis

## Root cause
- The actual culprit was aiosqlite's background worker thread
- aiosqlite creates a worker thread that blocks on queue.get() waiting for database operations
- Tests mocked the database with AsyncMock, so close() was never called
- The worker thread stayed alive, blocking threading._shutdown()

## Key insights
1. The obvious suspect (sounddevice) wasn't the actual problem
2. Mocking async database connections can hide cleanup issues
3. threading._shutdown() blocks on non-daemon threads that haven't exited
4. Database libraries often have background threads that need explicit cleanup

## Solution
- Added session-scoped autouse fixture to cleanup aiosqlite
- Added close_database() function to properly close connections
- Combined with lazy imports for sounddevice as preventive measure

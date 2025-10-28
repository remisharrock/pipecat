# Word Timestamp Feature Documentation

This directory contains comprehensive documentation for the word-level timestamp support feature in RTVI TTS messages.

## Files

### 📄 WORD_TIMESTAMP_FEATURE.md
**Detailed feature documentation** including:
- Overview of the problem and solution
- Message format specifications
- Client implementation guide
- TTS services support matrix
- Backward compatibility information

### 📄 SUMMARY.md
**Technical summary** covering:
- Root cause analysis
- Implementation details
- Modified classes and methods
- Testing approach
- Impact analysis

### 📄 FINAL_TASK_SUMMARY.md
**Complete task summary** with:
- Problem statement
- Root cause analysis
- Implementation details
- Testing and verification
- Security checks
- Backward compatibility guarantees

### 💻 client_example.ts
**TypeScript client examples** demonstrating:
- Simple immediate display (backward compatible)
- Time-synchronized subtitle display
- Karaoke-style word highlighting
- RTVI client integration

## Quick Start

### For Server Developers
The feature is automatically enabled. All TTS services using `WordTTSService` will include timestamps in `bot-tts-text` messages:

```python
# No code changes needed - timestamps are automatically included!
tts = AzureTTSService(...)  # Works with Azure
tts = CartesiaTTSService(...)  # Works with Cartesia
tts = ElevenLabsTTSService(...)  # Works with ElevenLabs
```

### For Client Developers
Check for the optional `timestamp` field in `bot-tts-text` messages:

```typescript
onBotTtsText(data) {
  const { text, timestamp } = data;
  
  if (timestamp !== undefined) {
    // New: schedule text display at specific time
    scheduleTextDisplay(text, timestamp);
  } else {
    // Fallback: display immediately (backward compatible)
    displayText(text);
  }
}
```

## Message Format

### With Timestamp
```json
{
  "label": "rtvi-ai",
  "type": "bot-tts-text",
  "data": {
    "text": "hello",
    "timestamp": 1234567890
  }
}
```

### Without Timestamp (Backward Compatible)
```json
{
  "label": "rtvi-ai",
  "type": "bot-tts-text",
  "data": {
    "text": "hello"
  }
}
```

## Timestamp Format
- **Unit**: Nanoseconds
- **Reference**: Relative to TTS playback start
- **Conversion**: `seconds = timestamp / 1_000_000_000`

## Testing

Run the test suite:
```bash
python tests/test_word_timestamps.py
```

Tests cover:
- Messages with timestamps ✅
- Messages without timestamps (backward compatibility) ✅
- RTVIObserver integration ✅

## Supported TTS Services
- ✅ **Azure TTS** - Via word boundary events
- ✅ **Cartesia TTS** - Via timestamp messages
- ✅ **ElevenLabs TTS** - Via character alignment data

Any TTS service inheriting from `WordTTSService` automatically supports this feature.

## Implementation
- **File Modified**: `src/pipecat/processors/frameworks/rtvi.py`
- **Lines Changed**: ~20
- **Breaking Changes**: None
- **Backward Compatible**: Yes

## Security
- ✅ CodeQL analysis: 0 alerts
- ✅ No vulnerabilities introduced
- ✅ Code review completed

## Need Help?
Refer to:
1. `WORD_TIMESTAMP_FEATURE.md` for detailed feature documentation
2. `client_example.ts` for implementation examples
3. `SUMMARY.md` for technical details
4. `tests/test_word_timestamps.py` for code examples

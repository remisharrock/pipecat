# Summary of Changes

## Issue
Azure TTS (and other TTS services) were generating word boundaries with timestamps on the server side, but clients were only receiving the text without timing information. This prevented clients from synchronizing text display with audio playback.

## Root Cause
The `RTVIObserver` in `src/pipecat/processors/frameworks/rtvi.py` was converting `TTSTextFrame` (which has a `pts` presentation timestamp) to `RTVIBotTTSTextMessage` using `RTVITextMessageData`, which only contained a `text` field. The timestamp was being discarded.

## Solution
1. Created `RTVITTSTextMessageData` - a new data class specifically for TTS text messages that includes an optional `timestamp` field (in nanoseconds)
2. Updated `RTVIBotTTSTextMessage` to use `RTVITTSTextMessageData` instead of `RTVITextMessageData`
3. Modified `RTVIObserver` to include `frame.pts` when creating TTS text messages

## Implementation Details

### New Classes
- **RTVITTSTextMessageData**: Pydantic model with `text: str` and `timestamp: Optional[int]` fields

### Modified Classes
- **RTVIBotTTSTextMessage**: Changed data field type from `RTVITextMessageData` to `RTVITTSTextMessageData`

### Modified Methods
- **RTVIObserver.on_push_frame**: Updated to pass `frame.pts` when creating TTS text messages

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

## Backward Compatibility
- The `timestamp` field is optional
- When `timestamp` is `None` or not set, it's excluded from the JSON (via `exclude_none=True`)
- Existing clients that don't check for timestamps continue to work unchanged
- No breaking changes to the RTVI protocol

## Supported TTS Services
All TTS services that inherit from `WordTTSService` automatically support word timestamps:
- Azure TTS (`AzureTTSService`)
- Cartesia TTS (`CartesiaTTSService`)
- ElevenLabs TTS (`ElevenLabsTTSService`)

## Testing
Created comprehensive test suite (`test_word_timestamps.py`) that verifies:
1. Messages with timestamps are correctly formatted
2. Messages without timestamps work (backward compatibility)
3. RTVIObserver properly includes timestamps from frames

All tests pass successfully.

## Documentation
- `WORD_TIMESTAMP_FEATURE.md` - Detailed feature documentation
- `client_example.ts` - Example client implementations in TypeScript

## Files Modified
- `src/pipecat/processors/frameworks/rtvi.py` - Main implementation

## Files Added
- `test_word_timestamps.py` - Test suite
- `WORD_TIMESTAMP_FEATURE.md` - Feature documentation
- `client_example.ts` - Client implementation examples
- `SUMMARY.md` - This file

## Next Steps for Clients
Clients should be updated to check for and use the `timestamp` field in `bot-tts-text` messages:

```typescript
onBotTtsText(data) {
  const { text, timestamp } = data;
  
  if (timestamp !== undefined) {
    // Schedule text display at specific time
    scheduleTextDisplay(text, timestamp);
  } else {
    // Fallback: display immediately
    displayText(text);
  }
}
```

## Impact
- **Server**: Minimal change, just passes through existing timestamp data
- **Clients**: Can now synchronize text display with audio playback
- **Backward Compatibility**: Full - existing clients continue to work
- **Performance**: No performance impact

## References
- Original issue: https://github.com/pipecat-ai/pipecat/issues/2918#issuecomment-3453646919
- RTVI Protocol: https://docs.rtvi.ai/

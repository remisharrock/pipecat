# Word Timestamp Support in RTVI TTS Messages

## Overview

This enhancement adds word-level timestamp support to RTVI TTS text messages, allowing clients to synchronize text display with audio playback at the word level.

## Problem

Previously, when TTS services (Azure, Cartesia, ElevenLabs) generated word boundaries with timestamps on the server side:

1. The timestamps were correctly logged in server logs
2. BUT the client received only the text without timestamps
3. All words arrived at the client at once, without timing information
4. Clients couldn't synchronize text display with audio playback

**Example from Azure TTS logs:**
```
DEBUG | AzureTTSService#0: Word boundary - 'Avant' at 0.10s
DEBUG | AzureTTSService#0: Word boundary - 'de' at 0.30s
```

**What client received:**
```javascript
{text: 'Avant'}  // No timestamp!
{text: 'de'}     // No timestamp!
```

## Solution

Added timestamp field to RTVI TTS text messages:

### Changes Made

1. **New Data Class: `RTVITTSTextMessageData`**
   - Extends basic text data with optional `timestamp` field
   - Timestamp is in nanoseconds (presentation timestamp from frame.pts)
   - Maintains backward compatibility (timestamp is optional)

2. **Updated: `RTVIBotTTSTextMessage`**
   - Now uses `RTVITTSTextMessageData` instead of `RTVITextMessageData`
   - Preserves timestamp when available

3. **Updated: `RTVIObserver`**
   - Includes `frame.pts` when creating TTS text messages
   - Timestamps are only sent when available

### Message Format

**With timestamp:**
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

**Without timestamp (backward compatible):**
```json
{
  "label": "rtvi-ai",
  "type": "bot-tts-text",
  "data": {
    "text": "hello"
  }
}
```

## Client Implementation

Clients can now use the timestamp to display words at the correct time:

```typescript
onBotTtsText(data) {
  const { text, timestamp } = data;
  
  if (timestamp) {
    // Schedule text to appear at specific time
    scheduleTextDisplay(text, timestamp);
  } else {
    // Fallback: display immediately
    displayText(text);
  }
}
```

## Timestamp Format

- **Unit**: Nanoseconds
- **Reference**: Relative to the start of TTS playback
- **Conversion**: To convert to seconds: `seconds = timestamp / 1_000_000_000`

## TTS Services Support

All WordTTSService-based TTS implementations automatically support word timestamps:

- **Azure TTS**: ✓ Full support via word boundary events
- **Cartesia TTS**: ✓ Full support via timestamp messages
- **ElevenLabs TTS**: ✓ Full support via alignment data

## Backward Compatibility

- Existing clients that don't check for timestamps continue to work
- The timestamp field is optional and excluded when not present (`exclude_none=True`)
- No breaking changes to existing RTVI protocol

## Testing

Run the test script to verify functionality:

```bash
python test_word_timestamps.py
```

Tests cover:
1. Messages with timestamps
2. Messages without timestamps (backward compatibility)
3. RTVIObserver integration

## Related Files

- `src/pipecat/processors/frameworks/rtvi.py` - Main implementation
- `src/pipecat/services/tts_service.py` - WordTTSService base class
- `src/pipecat/services/azure/tts.py` - Azure TTS with word boundaries
- `src/pipecat/services/cartesia/tts.py` - Cartesia TTS with timestamps
- `src/pipecat/services/elevenlabs/tts.py` - ElevenLabs TTS with alignment

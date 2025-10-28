#!/usr/bin/env python3
"""
Test script to demonstrate word timestamps in RTVI TTS text messages.

This script simulates how word timestamps from TTS services are now
properly sent to clients via RTVI bot-tts-text messages.
"""

import asyncio
from pipecat.processors.frameworks.rtvi import (
    RTVITTSTextMessageData,
    RTVIBotTTSTextMessage,
    RTVIObserver,
    RTVIObserverParams,
)
from pipecat.frames.frames import TTSTextFrame
from pipecat.transports.base_output import BaseOutputTransport
from pipecat.observers.base_observer import FramePushed
from pipecat.processors.frame_processor import FrameDirection


class MockOutputTransport(BaseOutputTransport):
    """Mock output transport for testing."""

    def __init__(self):
        pass


async def test_tts_text_with_timestamp():
    """Test that TTSTextFrame with timestamp is properly converted to RTVI message."""
    print("Testing TTSTextFrame with timestamp conversion...")

    # Create a TTSTextFrame with text and timestamp
    frame = TTSTextFrame(text="hello")
    frame.pts = 1234567890  # nanoseconds timestamp

    # Create RTVITTSTextMessageData
    data = RTVITTSTextMessageData(text=frame.text, timestamp=frame.pts)
    print(f"Created RTVITTSTextMessageData: text='{data.text}', timestamp={data.timestamp}")

    # Create the RTVI message
    message = RTVIBotTTSTextMessage(data=data)
    print(f"Created RTVIBotTTSTextMessage: {message.model_dump(exclude_none=True)}")

    # Verify timestamp is preserved
    assert message.data.text == "hello"
    assert message.data.timestamp == 1234567890
    print("✓ Timestamp is correctly preserved in RTVI message")


async def test_tts_text_without_timestamp():
    """Test that TTSTextFrame without timestamp still works (backward compatibility)."""
    print("\nTesting TTSTextFrame without timestamp (backward compatibility)...")

    # Create a TTSTextFrame with text but no timestamp
    frame = TTSTextFrame(text="world")
    # pts defaults to None

    # Create RTVITTSTextMessageData without timestamp
    data = RTVITTSTextMessageData(text=frame.text, timestamp=frame.pts)
    print(f"Created RTVITTSTextMessageData: text='{data.text}', timestamp={data.timestamp}")

    # Create the RTVI message
    message = RTVIBotTTSTextMessage(data=data)
    print(f"Created RTVIBotTTSTextMessage: {message.model_dump(exclude_none=True)}")

    # Verify text is present and timestamp is None
    assert message.data.text == "world"
    assert message.data.timestamp is None
    print("✓ Message works without timestamp (backward compatible)")


async def test_rtvi_observer_integration():
    """Test that RTVIObserver properly sends timestamps."""
    print("\nTesting RTVIObserver integration...")

    messages_sent = []

    class TestObserver(RTVIObserver):
        async def send_rtvi_message(self, model, exclude_none=True):
            """Capture messages instead of sending them."""
            messages_sent.append(model.model_dump(exclude_none=exclude_none))

    # Create observer
    observer = TestObserver(params=RTVIObserverParams(bot_tts_enabled=True))

    # Create TTSTextFrame with timestamp
    frame = TTSTextFrame(text="test")
    frame.pts = 9876543210

    # Simulate frame push from BaseOutputTransport
    src = MockOutputTransport()
    event = FramePushed(
        source=src, frame=frame, direction=FrameDirection.UPSTREAM, timestamp=0, destination=None
    )

    # Process the frame
    await observer.on_push_frame(event)

    # Verify message was sent
    assert len(messages_sent) == 1
    msg = messages_sent[0]
    print(f"Message sent: {msg}")

    assert msg["type"] == "bot-tts-text"
    assert msg["data"]["text"] == "test"
    assert msg["data"]["timestamp"] == 9876543210
    print("✓ RTVIObserver correctly includes timestamp in messages")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Word Timestamp Tests for RTVI TTS Messages")
    print("=" * 60)

    await test_tts_text_with_timestamp()
    await test_tts_text_without_timestamp()
    await test_rtvi_observer_integration()

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

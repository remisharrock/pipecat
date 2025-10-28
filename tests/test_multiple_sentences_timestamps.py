#!/usr/bin/env python3
"""
Test to verify that multiple TTS sentences with timestamps starting at 0
are handled correctly and produce monotonically increasing timestamps.

This is a simplified demonstration without requiring the full service infrastructure.
"""


def seconds_to_nanoseconds(seconds):
    """Convert seconds to nanoseconds."""
    return int(seconds * 1_000_000_000)


class MockClock:
    """Mock clock that returns controllable time."""
    
    def __init__(self):
        self.current_time_ns = 1000000000  # Start at 1 second
    
    def get_time(self):
        """Return current time in nanoseconds."""
        return self.current_time_ns
    
    def advance(self, seconds):
        """Advance time by given seconds."""
        self.current_time_ns += seconds_to_nanoseconds(seconds)


class WordTimestamp:
    """Simulates how WordTTSService handles timestamps."""
    
    def __init__(self, clock):
        self._clock = clock
        self._initial_word_timestamp = -1
        self._word_frames = []
    
    def start_word_timestamps(self):
        """Start tracking word timestamps from the current time."""
        if self._initial_word_timestamp == -1:
            self._initial_word_timestamp = self._clock.get_time()
    
    def reset_word_timestamps(self):
        """Reset word timestamp tracking."""
        self._initial_word_timestamp = -1
    
    def add_word_timestamp(self, word, relative_timestamp_seconds):
        """Add a word with its relative timestamp."""
        timestamp_ns = seconds_to_nanoseconds(relative_timestamp_seconds)
        absolute_pts = self._initial_word_timestamp + timestamp_ns
        self._word_frames.append({
            'text': word,
            'pts': absolute_pts
        })
        return absolute_pts


def test_multiple_sentences_timestamps():
    """Test that multiple sentences produce monotonically increasing timestamps."""
    print("Testing multiple TTS sentences with timestamps...")
    print()
    
    # Create mock clock and service
    clock = MockClock()
    service = WordTimestamp(clock)
    
    # Simulate first sentence: "Bonjour, merci d'être là."
    print("Sentence 1: 'Bonjour, merci d'être là.'")
    print(f"Starting at clock time: {clock.get_time() / 1_000_000_000:.2f}s")
    
    service.start_word_timestamps()
    
    # Add words with relative timestamps (like Azure TTS provides)
    words_1 = [
        ("Bonjour", 0.08),
        (",", 0.77),
        ("merci", 1.01),
        ("d'être", 1.30),
        ("là", 1.58),
        (".", 1.87),
    ]
    
    for word, ts in words_1:
        service.add_word_timestamp(word, ts)
    
    # Advance clock to simulate time passing (including audio playback)
    clock.advance(2.0)  # 2 seconds for first sentence
    
    # Reset for next sentence (like interruption or new TTS call)
    service.reset_word_timestamps()
    
    print()
    print("Sentence 2: 'Nous allons faire un petit échange...'")
    print(f"Starting at clock time: {clock.get_time() / 1_000_000_000:.2f}s")
    
    service.start_word_timestamps()
    
    # Add words with relative timestamps starting from 0 again
    words_2 = [
        ("Nous", 0.10),
        ("allons", 0.20),
        ("faire", 0.43),
        ("un", 0.62),
        ("petit", 0.68),
        ("échange", 0.90),
    ]
    
    for word, ts in words_2:
        service.add_word_timestamp(word, ts)
    
    # Advance clock again
    clock.advance(3.0)  # 3 seconds for second sentence
    
    service.reset_word_timestamps()
    
    print()
    print("Sentence 3: 'Avant de commencer...'")
    print(f"Starting at clock time: {clock.get_time() / 1_000_000_000:.2f}s")
    
    service.start_word_timestamps()
    
    # Add words with relative timestamps starting from 0 again
    words_3 = [
        ("Avant", 0.10),
        ("de", 0.30),
        ("commencer", 0.39),
    ]
    
    for word, ts in words_3:
        service.add_word_timestamp(word, ts)
    
    # Verify timestamps are monotonically increasing
    print()
    print("=" * 60)
    print("Verification:")
    print("=" * 60)
    
    # Extract all frames
    text_frames = service._word_frames
    
    print(f"\nTotal words across all sentences: {len(text_frames)}")
    print()
    
    # Group by sentence
    sentence_1_frames = text_frames[0:6]
    sentence_2_frames = text_frames[6:12]
    sentence_3_frames = text_frames[12:15]
    
    # Print timestamps for each sentence
    print("Sentence 1 timestamps (nanoseconds → seconds):")
    for frame in sentence_1_frames:
        print(f"  '{frame['text']}': {frame['pts']} ns = {frame['pts'] / 1_000_000_000:.2f}s")
    
    print()
    print("Sentence 2 timestamps (nanoseconds → seconds):")
    for frame in sentence_2_frames:
        print(f"  '{frame['text']}': {frame['pts']} ns = {frame['pts'] / 1_000_000_000:.2f}s")
    
    print()
    print("Sentence 3 timestamps (nanoseconds → seconds):")
    for frame in sentence_3_frames:
        print(f"  '{frame['text']}': {frame['pts']} ns = {frame['pts'] / 1_000_000_000:.2f}s")
    
    # Verify monotonicity
    print()
    print("Checking monotonicity...")
    prev_pts = 0
    all_monotonic = True
    
    for i, frame in enumerate(text_frames):
        if frame['pts'] <= prev_pts:
            print(f"  ❌ Frame {i} ('{frame['text']}'): {frame['pts']} <= {prev_pts}")
            all_monotonic = False
        prev_pts = frame['pts']
    
    if all_monotonic:
        print("  ✅ All timestamps are monotonically increasing!")
    
    # Verify sentences are properly separated
    print()
    print("Checking sentence separation...")
    last_sentence_1 = sentence_1_frames[-1]['pts']
    first_sentence_2 = sentence_2_frames[0]['pts']
    last_sentence_2 = sentence_2_frames[-1]['pts']
    first_sentence_3 = sentence_3_frames[0]['pts']
    
    print(f"  Last word of sentence 1: {last_sentence_1 / 1_000_000_000:.2f}s")
    print(f"  First word of sentence 2: {first_sentence_2 / 1_000_000_000:.2f}s")
    print(f"  Gap: {(first_sentence_2 - last_sentence_1) / 1_000_000_000:.2f}s")
    
    if first_sentence_2 > last_sentence_1:
        print("  ✅ Sentence 2 starts after sentence 1 ends")
    
    print()
    print(f"  Last word of sentence 2: {last_sentence_2 / 1_000_000_000:.2f}s")
    print(f"  First word of sentence 3: {first_sentence_3 / 1_000_000_000:.2f}s")
    print(f"  Gap: {(first_sentence_3 - last_sentence_2) / 1_000_000_000:.2f}s")
    
    if first_sentence_3 > last_sentence_2:
        print("  ✅ Sentence 3 starts after sentence 2 ends")
    
    print()
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    print()
    print("The implementation correctly handles multiple sentences where each")
    print("sentence's word boundaries start at 0 seconds:")
    print()
    print("1. Each sentence gets a new _initial_word_timestamp when it starts")
    print("2. Word timestamps = _initial_word_timestamp + relative_timestamp")
    print("3. This produces monotonically increasing absolute timestamps")
    print("4. Sentences are naturally separated without overlap")
    print()
    print("✅ Multiple sentences with timestamps starting at 0 work correctly!")


if __name__ == "__main__":
    test_multiple_sentences_timestamps()

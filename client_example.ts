/**
 * Example Client Implementation for Word Timestamps
 * 
 * This example shows how to handle bot-tts-text messages with timestamps
 * in a JavaScript/TypeScript client.
 */

interface BotTtsTextData {
  text: string;
  timestamp?: number; // Optional: nanoseconds since TTS started
}

interface RTVIMessage {
  label: string;
  type: string;
  data: BotTtsTextData;
}

/**
 * Example 1: Simple immediate display (backward compatible)
 */
function handleBotTtsTextSimple(data: BotTtsTextData) {
  console.log('[TTS Text]', data.text);
  displaySubtitle(data.text);
}

/**
 * Example 2: Time-synchronized display with timestamps
 */
class TimedSubtitleDisplay {
  private startTime: number | null = null;
  private subtitleQueue: Array<{ text: string; timestamp: number }> = [];
  private displayTimer: number | null = null;

  onBotTtsText(data: BotTtsTextData) {
    console.log('[TTS Text]', {
      text: data.text,
      timestamp: data.timestamp ? `${(data.timestamp / 1_000_000_000).toFixed(2)}s` : 'none'
    });

    if (data.timestamp !== undefined) {
      // Schedule display at specific time
      this.scheduleSubtitle(data.text, data.timestamp);
    } else {
      // Fallback: display immediately
      this.displaySubtitle(data.text);
    }
  }

  onBotTtsStarted() {
    // Reset timing reference when TTS starts
    this.startTime = Date.now();
    this.subtitleQueue = [];
  }

  onBotTtsStopped() {
    // Clear any pending subtitles
    if (this.displayTimer) {
      clearTimeout(this.displayTimer);
      this.displayTimer = null;
    }
    this.startTime = null;
  }

  private scheduleSubtitle(text: string, timestampNs: number) {
    if (!this.startTime) {
      this.startTime = Date.now();
    }

    // Convert nanoseconds to milliseconds
    const timestampMs = timestampNs / 1_000_000;
    const elapsed = Date.now() - this.startTime;
    const delay = Math.max(0, timestampMs - elapsed);

    this.displayTimer = setTimeout(() => {
      this.displaySubtitle(text);
    }, delay);
  }

  private displaySubtitle(text: string) {
    // Update subtitle display
    const subtitleElement = document.getElementById('subtitles');
    if (subtitleElement) {
      subtitleElement.textContent += text + ' ';
    }
  }
}

/**
 * Example 3: Using timestamps for karaoke-style highlighting
 */
class KaraokeSubtitleDisplay {
  private words: Array<{ text: string; timestamp: number }> = [];
  private currentIndex = 0;
  private startTime: number | null = null;
  private highlightTimer: number | null = null;

  onBotTtsText(data: BotTtsTextData) {
    if (data.timestamp !== undefined) {
      this.words.push({ text: data.text, timestamp: data.timestamp });
    }
  }

  onBotTtsStarted() {
    this.words = [];
    this.currentIndex = 0;
    this.startTime = Date.now();
  }

  onBotTtsStopped() {
    // Start highlighting words as they're spoken
    this.scheduleNextHighlight();
  }

  private scheduleNextHighlight() {
    if (this.currentIndex >= this.words.length || !this.startTime) {
      return;
    }

    const word = this.words[this.currentIndex];
    const timestampMs = word.timestamp / 1_000_000;
    const elapsed = Date.now() - this.startTime;
    const delay = Math.max(0, timestampMs - elapsed);

    this.highlightTimer = setTimeout(() => {
      this.highlightWord(this.currentIndex);
      this.currentIndex++;
      this.scheduleNextHighlight();
    }, delay);
  }

  private highlightWord(index: number) {
    const wordElement = document.getElementById(`word-${index}`);
    if (wordElement) {
      wordElement.classList.add('highlighted');
    }
  }
}

/**
 * Example 4: Integration with RTVI client
 */
const rtviClient = {
  // ... other RTVI client setup ...

  callbacks: {
    onBotTtsText: (data: BotTtsTextData) => {
      console.log('[CALLBACK] Bot TTS text received:', data);
      
      // Check if timestamp is available
      if (data.timestamp) {
        // New behavior: use timestamp for synchronization
        const timeSeconds = data.timestamp / 1_000_000_000;
        console.log(`  Word: "${data.text}" at ${timeSeconds.toFixed(2)}s`);
        scheduleWordDisplay(data.text, data.timestamp);
      } else {
        // Old behavior: display immediately (backward compatible)
        console.log(`  Word: "${data.text}" (no timestamp)`);
        displayWordImmediate(data.text);
      }
    },

    onBotTtsStarted: () => {
      console.log('[CALLBACK] Bot TTS started');
      resetSubtitleDisplay();
    },

    onBotTtsStopped: () => {
      console.log('[CALLBACK] Bot TTS stopped');
    }
  }
};

/**
 * Example message from server (with timestamp):
 * {
 *   "label": "rtvi-ai",
 *   "type": "bot-tts-text",
 *   "data": {
 *     "text": "hello",
 *     "timestamp": 1234567890
 *   }
 * }
 * 
 * Example message from server (without timestamp - backward compatible):
 * {
 *   "label": "rtvi-ai",
 *   "type": "bot-tts-text",
 *   "data": {
 *     "text": "hello"
 *   }
 * }
 */

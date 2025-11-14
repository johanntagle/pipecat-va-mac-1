# LLM Text Filtering for TTS

This document describes the text filtering system that cleans LLM output before it's sent to the Text-to-Speech (TTS) service.

## Overview

LLMs often include formatting characters and markdown in their responses (asterisks for emphasis, underscores, etc.) that shouldn't be spoken aloud. The `LLMTextFilter` processor removes these characters before the text reaches the TTS service.

## What Gets Filtered

The text filter removes:

1. **Markdown formatting:**
   - `**bold**` → `bold`
   - `__bold__` → `bold`
   - `*italic*` → `italic`
   - `_italic_` → `italic`
   - `~~strikethrough~~` → `strikethrough`

2. **Standalone special characters:**
   - Asterisks (`*`)
   - Underscores (`_`)

3. **Markdown headers:**
   - `# Header` → `Header`
   - `## Subheader` → `Subheader`

4. **Code formatting:**
   - `` `code` `` → `code`
   - Code blocks (```````) are removed entirely

5. **Markdown links:**
   - `[text](url)` → `text`

6. **Excessive whitespace:**
   - Multiple spaces → single space
   - Leading/trailing whitespace trimmed

## Implementation

### File: `server/text_filter.py`

The `LLMTextFilter` class extends Pipecat's `FrameProcessor`:

```python
class LLMTextFilter(FrameProcessor):
    """
    Filters and cleans text from LLM output before it goes to TTS.
    """

    def clean_text(self, text: str) -> str:
        """Apply all filter patterns to clean the text."""
        # Uses compiled regex patterns for efficiency
        # Returns cleaned text suitable for TTS

    async def process_frame(self, frame: Frame, direction):
        """Process frames, filtering TextFrames before they reach TTS."""
        # Filters TextFrame objects (LLM output)
        # Passes through LLMFullResponseEndFrame (signals completion)
        # Passes through all other frame types unchanged
```

### Critical: LLMFullResponseEndFrame Handling

The filter **must** pass through `LLMFullResponseEndFrame` immediately. This frame signals to downstream processors (like TTS) that the LLM has finished generating its response and they should flush any buffered content.

**Without this:**
- The last sentence of the LLM response gets held in TTS buffer
- TTS waits for more text that never comes
- The last sentence only plays when the user speaks again (triggering a new LLM response)

**With this:**
- `LLMFullResponseEndFrame` signals completion
- TTS immediately flushes and speaks the last sentence
- Natural conversation flow is maintained

### Integration in Pipeline

The text filter is placed in the pipeline between the LLM and TTS:

```python
pipeline = Pipeline([
    transport.input(),
    stt,                          # Speech-to-Text
    rtvi,
    context_aggregator.user(),
    llm,                          # LLM generates response
    text_filter,                  # ← Clean text here
    tts,                          # Text-to-Speech
    transport.output(),
    context_aggregator.assistant(),
])
```

## Examples

### Example 1: Emphasis Removal
**LLM Output:**
```
I'm *really* excited to help you with **that**!
```

**Filtered Output:**
```
I'm really excited to help you with that!
```

### Example 2: Action Descriptions
**LLM Output:**
```
*smiles* Sure, I can help you with that!
```

**Filtered Output:**
```
smiles Sure, I can help you with that!
```

### Example 3: Markdown Formatting
**LLM Output:**
```
Here are the steps:
1. **First**, do this
2. _Then_, do that
```

**Filtered Output:**
```
Here are the steps:
1. First, do this
2. Then, do that
```

## Logging

The filter logs when it makes changes:

```
DEBUG: Text filter: '*really* excited' -> 'really excited'
INFO: Filtered text: 'I'm *really* excited!' -> 'I'm really excited!'
```

## Customization

To add or modify filtering rules, edit `server/text_filter.py`:

```python
self._patterns = [
    # Add your custom pattern here
    (re.compile(r'your_pattern'), r'replacement'),
    
    # Existing patterns...
]
```

### Common Customizations

**Remove emojis:**
```python
(re.compile(r'[\U00010000-\U0010ffff]'), ''),
```

**Remove parenthetical asides:**
```python
(re.compile(r'\([^)]+\)'), ''),
```

**Convert numbers to words:**
```python
# This would require a more complex function
# Consider using a library like num2words
```

## Testing

To test the text filter:

1. **Start the server:**
   ```bash
   cd server
   uv run python 02_db_backed.py 1
   ```

2. **Prompt the LLM to use formatting:**
   - "Can you emphasize the word 'important' in your response?"
   - "Use asterisks to show excitement"

3. **Check the logs:**
   - Look for "Filtered text:" messages
   - Verify the spoken output doesn't include special characters

4. **Listen to the TTS output:**
   - The voice should not say "asterisk" or "underscore"
   - Emphasis should be natural, not literal

## Performance

- Uses compiled regex patterns for efficiency
- Minimal overhead (~1-2ms per text chunk)
- Processes text synchronously (no async overhead)
- No external dependencies

## Troubleshooting

### Last Sentence Not Spoken Until User Speaks Again

**Symptom**: The agent stops speaking before the last sentence, then speaks it only when the user starts talking again. When interrupted, the agent's next response starts with the last sentence from the previous response.

**Root Cause**: Pipecat's `TTSService` has built-in sentence aggregation (`aggregate_sentences=True` by default) that buffers text until it detects a complete sentence. The last sentence gets held in the buffer waiting for more text that never comes.

**The Problem with Simple Solutions**:
- ❌ `aggregate_sentences=False` → TTS speaks word-by-word (terrible quality, see error.log)
- ❌ Keep `aggregate_sentences=True` → Last sentence gets stuck in buffer
- ✅ **Custom sentence aggregator that flushes on `LLMFullResponseEndFrame`** → Natural sentences + immediate completion

**Solution - Custom Sentence Aggregator (RECOMMENDED)**:

Use the custom `SentenceAggregator` processor that:
1. Buffers text into complete sentences (natural speech)
2. Flushes immediately when it receives `LLMFullResponseEndFrame` (no stuck sentences)

**Implementation** (`server/sentence_aggregator.py`):

```python
from sentence_aggregator import SentenceAggregator

# Disable built-in TTS aggregation
tts = TTSMLXIsolated(
    model="mlx-community/Kokoro-82M-bf16",
    voice="af_heart",
    sample_rate=24000,
    aggregate_sentences=False  # We use custom aggregator instead
)

# Create sentence aggregator
sentence_aggregator = SentenceAggregator()

# Pipeline order is critical
pipeline = Pipeline([
    # ...
    llm,
    text_filter,           # Clean text first
    sentence_aggregator,   # Then aggregate into sentences
    tts,                   # Then speak
    # ...
])
```

**How It Works**:
1. LLM streams tokens: "Hello", " there", "!", " How", " can", " I", " help", "?"
2. Text filter cleans each token
3. Sentence aggregator buffers: "Hello there!"
4. When it sees "!" (sentence end), it flushes to TTS
5. Continues buffering: "How can I help?"
6. When `LLMFullResponseEndFrame` arrives, flushes remaining text
7. TTS speaks complete sentences naturally

**Verification**:
- Test by asking a question and verifying the complete response is spoken immediately
- The agent should not wait for you to speak before finishing its response
- When you interrupt, the next response should NOT start with the previous last sentence
- Check logs for:
  ```
  SentenceAggregator: Detected sentence end
  SentenceAggregator: Flushing buffer: 'Hello there!'
  SentenceAggregator: Received LLMFullResponseEndFrame, flushing buffer
  ```

### Text Filter Not Working

**Symptom**: Agent reads asterisks, underscores, or other markdown symbols

**Possible causes:**
- Check that `text_filter.py` is in the `server/` directory
- Verify the import in `02_db_backed.py` or `03_rag.py`
- Check logs for any errors during initialization
- Ensure filter is in the pipeline between LLM and TTS

**Solution:**
```python
# Verify pipeline order in run_bot():
pipeline = Pipeline([
    # ...
    llm,
    text_filter,  # Must be AFTER llm, BEFORE tts
    tts,
    # ...
])
```

### Too Much Text Being Removed

**Symptom**: Important words or phrases are missing from spoken output

**Solution:**
- Review the regex patterns in `text_filter.py`
- Adjust patterns to be more specific
- Test with sample inputs
- Check logs to see what's being filtered

### Not Enough Text Being Removed

**Symptom**: Agent still reads unwanted symbols or formatting

**Solution:**
- Add additional patterns to `self._patterns`
- Check the LLM output format in logs
- Consider updating the system prompt to discourage certain formatting
- Test patterns with regex tools before adding


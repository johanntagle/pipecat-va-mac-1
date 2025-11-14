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
        # Only filters TextFrame objects
        # Passes through all other frame types unchanged
```

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

**Text filter not working:**
- Check that `text_filter.py` is in the `server/` directory
- Verify the import in `02_db_backed.py`
- Check logs for any errors during initialization

**Too much text being removed:**
- Review the regex patterns in `text_filter.py`
- Adjust patterns to be more specific
- Test with sample inputs

**Not enough text being removed:**
- Add additional patterns to `self._patterns`
- Check the LLM output format
- Consider updating the system prompt to discourage certain formatting


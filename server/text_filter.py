"""
Text filter processor for cleaning LLM output before TTS.

This processor removes unwanted characters and formatting that shouldn't be spoken,
such as asterisks, markdown formatting, and other special characters.
"""

import re

from loguru import logger
from pipecat.frames.frames import Frame, TextFrame
from pipecat.processors.frame_processor import FrameProcessor


class LLMTextFilter(FrameProcessor):
    """
    Filters and cleans text from LLM output before it goes to TTS.
    
    Removes:
    - Asterisks (*) used for emphasis or actions
    - Underscores (_) used for emphasis
    - Markdown formatting (**, __, ~~, etc.)
    - Excessive whitespace
    - Other non-speakable characters
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Compile regex patterns for efficiency
        # Order matters! More specific patterns first, then cleanup
        self._patterns = [
            # Remove markdown bold/italic - keep the text inside
            (re.compile(r'\*\*([^*]+)\*\*'), r'\1'),  # **bold** -> bold
            (re.compile(r'__([^_]+)__'), r'\1'),      # __bold__ -> bold
            (re.compile(r'\*([^*]+)\*'), r'\1'),      # *italic* -> italic
            (re.compile(r'_([^_]+)_'), r'\1'),        # _italic_ -> italic

            # Remove strikethrough
            (re.compile(r'~~([^~]+)~~'), r'\1'),      # ~~text~~ -> text

            # Remove markdown headers
            (re.compile(r'^#+\s*'), ''),              # # Header -> Header

            # Remove markdown code blocks
            (re.compile(r'```[^`]*```'), ''),         # Remove code blocks
            (re.compile(r'`([^`]+)`'), r'\1'),        # `code` -> code

            # Remove markdown links but keep text
            (re.compile(r'\[([^\]]+)\]\([^)]+\)'), r'\1'),  # [text](url) -> text

            # Remove any remaining standalone asterisks/underscores
            (re.compile(r'\*+'), ''),                 # Remove remaining asterisks
            (re.compile(r'_+'), ''),                  # Remove remaining underscores

            # Clean up excessive whitespace (must be last)
            (re.compile(r'\s+'), ' '),                # Multiple spaces -> single space
        ]

    def clean_text(self, text: str) -> str:
        """
        Clean the text by applying all filter patterns.

        Args:
            text: Raw text from LLM (may be a streaming token)

        Returns:
            Cleaned text suitable for TTS
        """
        if not text:
            return text

        cleaned = text

        # Apply all regex patterns
        for pattern, replacement in self._patterns:
            cleaned = pattern.sub(replacement, cleaned)

        # DO NOT strip leading/trailing whitespace!
        # The LLM streams tokens like " your" and " friendly"
        # and we need to preserve those spaces for proper word separation

        # Log if significant changes were made
        if cleaned != text:
            logger.debug(f"Text filter: '{text}' -> '{cleaned}'")

        return cleaned

    async def process_frame(self, frame: Frame, direction):
        """
        Process frames, filtering TextFrames before they reach TTS.

        Args:
            frame: The frame to process
            direction: Frame direction
        """
        # ✅ Required: Call parent to handle system frames properly
        await super().process_frame(frame, direction)

        # Only filter TextFrames (which contain LLM output)
        if isinstance(frame, TextFrame):
            original_text = frame.text
            logger.debug(f"LLMTextFilter received: '{original_text}' (len={len(original_text)})")
            cleaned_text = self.clean_text(original_text)
            logger.debug(f"LLMTextFilter cleaned: '{cleaned_text}' (len={len(cleaned_text)})")

            # Create a new TextFrame with cleaned text
            if cleaned_text != original_text:
                logger.info(f"Filtered text: '{original_text}' -> '{cleaned_text}'")
                await self.push_frame(TextFrame(text=cleaned_text), direction)
            else:
                logger.debug(f"LLMTextFilter: No changes needed, passing through")
                await self.push_frame(frame, direction)
        else:
            # Pass through all other frame types unchanged
            await self.push_frame(frame, direction)


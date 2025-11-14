"""
Sentence aggregator that flushes on LLMFullResponseEndFrame.

This processor aggregates text into complete sentences before sending to TTS,
but immediately flushes any buffered text when it receives an LLMFullResponseEndFrame.
This ensures natural speech (full sentences) while avoiding the "last sentence stuck" problem.
"""

import re
from loguru import logger
from pipecat.frames.frames import Frame, TextFrame, LLMFullResponseEndFrame
from pipecat.processors.frame_processor import FrameProcessor


class SentenceAggregator(FrameProcessor):
    """
    Aggregates text into sentences, flushing on sentence boundaries or LLMFullResponseEndFrame.
    
    This solves the problem where:
    - Without aggregation: TTS speaks word-by-word (terrible quality)
    - With default aggregation: Last sentence gets stuck in buffer
    - With this aggregator: Natural sentences + immediate flush on completion
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._buffer = ""
        
        # Sentence-ending punctuation
        self._sentence_endings = re.compile(r'[.!?]\s*$')
        
    def _is_sentence_end(self, text: str) -> bool:
        """Check if text ends with sentence-ending punctuation."""
        return bool(self._sentence_endings.search(text))
    
    async def _flush_buffer(self, direction):
        """Flush the current buffer as a TextFrame."""
        if self._buffer.strip():
            logger.debug(f"SentenceAggregator: Flushing buffer: '{self._buffer}'")
            await self.push_frame(TextFrame(text=self._buffer), direction)
            self._buffer = ""
    
    async def process_frame(self, frame: Frame, direction):
        """
        Process frames, aggregating text until sentence boundaries or end signal.
        
        Args:
            frame: The frame to process
            direction: Frame direction
        """
        await super().process_frame(frame, direction)
        
        if isinstance(frame, TextFrame):
            # Add to buffer
            self._buffer += frame.text
            logger.debug(f"SentenceAggregator: Buffer now: '{self._buffer}'")
            
            # Check if we have a complete sentence
            if self._is_sentence_end(self._buffer):
                logger.debug(f"SentenceAggregator: Detected sentence end")
                await self._flush_buffer(direction)
            # Otherwise keep buffering
            
        elif isinstance(frame, LLMFullResponseEndFrame):
            # CRITICAL: Flush any remaining text when LLM is done
            logger.debug("SentenceAggregator: Received LLMFullResponseEndFrame, flushing buffer")
            await self._flush_buffer(direction)
            # Pass through the end frame
            await self.push_frame(frame, direction)
            
        else:
            # Pass through all other frame types
            await self.push_frame(frame, direction)


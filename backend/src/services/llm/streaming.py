"""
Streaming implementation for LLM responses.
Supports both synchronous and asynchronous streaming from providers.
Yields chunks in real-time with no output buffering for minimal latency.
"""

from typing import AsyncGenerator, Generator, Union, Any, Iterator
import asyncio
import inspect
from concurrent.futures import ThreadPoolExecutor
from src.core.exceptions import LLMError


# Thread pool for running sync iterators without blocking event loop
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="stream_sync_")

# Sentinel object for detecting iterator exhaustion (safer than StopIteration)
_SENTINEL = object()


class StreamingHandler:
    """
    Handler for true streaming responses.
    Yields chunks immediately with no output buffering.
    Accumulates chunks only for persistence (database storage).
    """
    
    def __init__(self):
        """Initialize streaming handler."""
        self.full_response: list[str] = []
    
    async def stream_chunks(
        self,
        chunk_source: Union[AsyncGenerator[str, None], Generator[str, None, None], Any]
    ) -> AsyncGenerator[str, None]:
        """
        Stream chunks in real-time with no output buffering.
        Supports both sync and async chunk sources.
        
        Args:
            chunk_source: Async generator, sync generator, or iterable yielding text chunks
            
        Yields:
            Text chunks as they arrive (no buffering)
            
        Raises:
            LLMError: If chunk source is invalid or streaming fails
        """
        try:
            # Reject strings and bytes (would iterate character-by-character)
            if isinstance(chunk_source, (str, bytes)):
                raise LLMError(
                    f"Invalid chunk source: got {type(chunk_source).__name__}, "
                    "expected async/sync generator or iterable of chunks"
                )
            
            # Handle async generators and async iterables
            if inspect.isasyncgen(chunk_source) or hasattr(chunk_source, "__aiter__"):
                async for chunk in chunk_source:
                    chunk = self._normalize_chunk(chunk)
                    if chunk:
                        self.full_response.append(chunk)
                        yield chunk
                return
            
            # Handle sync generators and sync iterables
            if inspect.isgenerator(chunk_source) or hasattr(chunk_source, "__iter__"):
                async for chunk in self._run_sync_iterable_async(chunk_source):
                    chunk = self._normalize_chunk(chunk)
                    if chunk:
                        self.full_response.append(chunk)
                        yield chunk
                return
            
            raise LLMError(f"Unsupported chunk source type: {type(chunk_source)}")
                
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"Streaming error: {str(e)}")
    
    def _normalize_chunk(self, chunk: Any) -> str:
        """
        Normalize chunk to string.
        Only accepts str, bytes, or None. Ignores other types for safety.
        
        Args:
            chunk: Raw chunk (str, bytes, None, or other)
            
        Returns:
            Normalized string chunk, or empty string for unknown types
        """
        if chunk is None:
            return ""
        if isinstance(chunk, bytes):
            return chunk.decode("utf-8", errors="replace")
        if isinstance(chunk, str):
            return chunk
        # Safer default: ignore unknown chunk types (don't stringify arbitrary objects)
        return ""
    
    async def _run_sync_iterator_async(
        self,
        it: Iterator[Any]
    ) -> AsyncGenerator[Any, None]:
        """
        Run sync iterator in thread pool to avoid blocking event loop.
        
        Args:
            it: Synchronous iterator
            
        Yields:
            Items from iterator
        """
        loop = asyncio.get_running_loop()
        
        while True:
            # Use sentinel instead of StopIteration for safe exhaustion detection
            item = await loop.run_in_executor(_executor, next, it, _SENTINEL)
            
            if item is _SENTINEL:
                break
            
            yield item
    
    async def _run_sync_iterable_async(
        self,
        iterable: Any
    ) -> AsyncGenerator[Any, None]:
        """
        Run sync iterable in thread pool to avoid blocking event loop.
        
        Args:
            iterable: Synchronous iterable
            
        Yields:
            Items from iterable
        """
        loop = asyncio.get_running_loop()
        
        # Convert to iterator in thread pool
        it = await loop.run_in_executor(_executor, iter, iterable)
        
        # Iterate using the iterator helper
        async for item in self._run_sync_iterator_async(it):
            yield item
    
    def get_full_response(self) -> str:
        """
        Get the complete response after streaming is done.
        Used for storing in database.
        
        Returns:
            Complete response text
        """
        return "".join(self.full_response).strip()
    
    def reset(self) -> None:
        """Reset the handler for reuse."""
        self.full_response = []


async def stream_openai_response(stream: Any) -> AsyncGenerator[str, None]:
    """
    Stream OpenAI response chunks.
    Supports both sync and async OpenAI streams.
    
    Args:
        stream: OpenAI streaming response (sync or async)
        
    Yields:
        Text chunks from OpenAI
    """
    try:
        # Handle async stream
        if inspect.isasyncgen(stream) or hasattr(stream, "__aiter__"):
            async for chunk in stream:
                # Safe attribute access
                if not chunk.choices:
                    continue
                
                delta = chunk.choices[0].delta
                text = getattr(delta, "content", None)
                
                if text:
                    yield text
        
        # Handle sync stream (run in thread pool)
        else:
            loop = asyncio.get_running_loop()
            it = await loop.run_in_executor(_executor, iter, stream)
            
            while True:
                # Use sentinel for safe exhaustion detection
                chunk = await loop.run_in_executor(_executor, next, it, _SENTINEL)
                
                if chunk is _SENTINEL:
                    break
                
                # Safe attribute access
                if not chunk.choices:
                    continue
                
                delta = chunk.choices[0].delta
                text = getattr(delta, "content", None)
                
                if text:
                    yield text
                    
    except Exception as e:
        raise LLMError(f"OpenAI streaming error: {str(e)}")


async def stream_gemini_response(response: Any) -> AsyncGenerator[str, None]:
    """
    Stream Gemini response chunks.
    Supports both sync and async Gemini streams.
    
    Args:
        response: Gemini streaming response (sync or async)
        
    Yields:
        Text chunks from Gemini
    """
    try:
        # Handle async stream
        if inspect.isasyncgen(response) or hasattr(response, "__aiter__"):
            async for chunk in response:
                # Safe attribute access
                text = getattr(chunk, "text", None)
                
                if text:
                    yield text
        
        # Handle sync stream (run in thread pool)
        else:
            loop = asyncio.get_running_loop()
            it = await loop.run_in_executor(_executor, iter, response)
            
            while True:
                # Use sentinel for safe exhaustion detection
                chunk = await loop.run_in_executor(_executor, next, it, _SENTINEL)
                
                if chunk is _SENTINEL:
                    break
                
                # Safe attribute access
                text = getattr(chunk, "text", None)
                
                if text:
                    yield text
                    
    except Exception as e:
        raise LLMError(f"Gemini streaming error: {str(e)}")


def get_streaming_handler() -> StreamingHandler:
    """
    Get a new StreamingHandler instance.
    
    Returns:
        StreamingHandler instance
    """
    return StreamingHandler()


def shutdown_streaming_executor() -> None:
    """
    Shutdown the thread pool executor.
    Call this on application shutdown for clean resource cleanup.
    """
    _executor.shutdown(wait=True)

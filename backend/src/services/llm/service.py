from typing import List, Dict, Any, Optional, Callable, AsyncGenerator, Union
import asyncio
import time

from openai import OpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from src.config import settings
from src.core.exceptions import LLMError
from src.core.schemas.user import UserResponse
from src.core.schemas.profile import ProfileResponse
from src.core.schemas.product import ProductResponse
from src.repositories.user import UserRepository
from src.repositories.profile import ProfileRepository
from src.services.llm.prompts import PromptBuilder
from src.services.llm.streaming import (
    get_streaming_handler,
    stream_openai_response,
    stream_gemini_response
)
from src.services.llm.intent_analyzer import IntentAnalyzer

class LLMService:
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.profile_repo = ProfileRepository()
        self.prompt_builder = PromptBuilder()
        self.intent_analyzer = IntentAnalyzer()
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        try:
            if settings.llm.provider == "openai":
                self._client = OpenAI(
                    api_key=settings.llm.openai.api_key,
                    timeout=settings.llm.openai.timeout,
                    max_retries=0
                )
            else:
                genai.configure(api_key=settings.llm.gemini.api_key)
                self._client = genai.GenerativeModel(
                    model_name=settings.llm.gemini.model,
                    generation_config={
                        'temperature': settings.llm.gemini.temperature,
                        'top_p': settings.llm.gemini.top_p,
                        'top_k': settings.llm.gemini.top_k,
                        'max_output_tokens': settings.llm.gemini.max_tokens,
                    },
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
        except Exception as e:
            raise LLMError(f"Failed to initialize LLM client: {str(e)}")
    
    async def generate_response(
        self,
        user_id: str,
        messages: List[Dict[str, str]],
        available_products: Optional[List[ProductResponse]] = None,
        full_catalog: Optional[List[ProductResponse]] = None,
        conversation_stage: str = "discovery",
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate LLM response with optional streaming.
        
        Args:
            user_id: User ID
            messages: Conversation messages
            available_products: Filtered products (TIER 2)
            full_catalog: Complete product catalog (TIER 1)
            conversation_stage: Current conversation stage
            stream: If True, returns AsyncGenerator for streaming
            
        Returns:
            str if stream=False, AsyncGenerator[str, None] if stream=True
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            profile = self.profile_repo.get_by_user_id(user_id)
            
            user_response = UserResponse(**user)
            profile_response = ProfileResponse(**profile) if profile else None
            
            system_prompt = self.prompt_builder.build_system_prompt(
                user=user_response,
                profile=profile_response,
                available_products=available_products or [],
                conversation_stage=conversation_stage,
                full_catalog=full_catalog
            )
            
            formatted_messages = self._prepare_messages(system_prompt, messages)
            
            if stream:
                if settings.llm.provider == "openai":
                    return self._call_openai_streaming(formatted_messages)
                else:
                    return self._call_gemini_streaming(formatted_messages)
            else:
                if settings.llm.provider == "openai":
                    return await self._call_openai_with_retry_async(formatted_messages)
                else:
                    return await self._call_gemini_with_retry_async(formatted_messages)
                
        except Exception as e:
            raise LLMError(f"Failed to generate response: {str(e)}")

    def _prepare_messages(
        self,
        system_prompt: str,
        conversation_messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": system_prompt}]
        
        context_window = settings.conversation.context_window_messages
        recent_messages = conversation_messages[-context_window:] if len(conversation_messages) > context_window else conversation_messages
        
        messages.extend(recent_messages)
        
        return messages
    
    def _call_openai(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = self._client.chat.completions.create(
                model=settings.llm.openai.model,
                messages=messages,
                temperature=settings.llm.openai.temperature,
                max_tokens=settings.llm.openai.max_tokens,
                top_p=settings.llm.openai.top_p,
                frequency_penalty=settings.llm.openai.frequency_penalty,
                presence_penalty=settings.llm.openai.presence_penalty,
            )
            
            if not response.choices:
                raise LLMError("No response from OpenAI")
            
            content = response.choices[0].message.content
            if not content:
                raise LLMError("Empty response from OpenAI")
            
            return content.strip()
            
        except RateLimitError as e:
            raise LLMError(f"Rate limit exceeded: {str(e)}")
        except APITimeoutError as e:
            raise LLMError(f"Request timed out: {str(e)}")
        except APIConnectionError as e:
            raise LLMError(f"Connection error: {str(e)}")
        except APIError as e:
            raise LLMError(f"API error: {str(e)}")
        except Exception as e:
            raise LLMError(f"Unexpected error: {str(e)}")
    
    def _call_gemini(self, messages: List[Dict[str, str]]) -> str:
        try:
            formatted_prompt = self._format_messages_for_gemini(messages)
            response = self._client.generate_content(formatted_prompt)
            
            if not response.text:
                raise LLMError("Empty response from Gemini")
            
            return response.text.strip()
            
        except Exception as e:
            error_msg = str(e)
            if 'quota' in error_msg.lower() or 'rate' in error_msg.lower():
                raise LLMError(f"Rate limit exceeded: {error_msg}")
            elif 'timeout' in error_msg.lower():
                raise LLMError(f"Request timed out: {error_msg}")
            else:
                raise LLMError(f"Gemini error: {error_msg}")
    
    def _format_messages_for_gemini(self, messages: List[Dict[str, str]]) -> str:
        system_content = ""
        conversation_parts = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "system":
                system_content = content
            elif role == "user":
                conversation_parts.append(f"User: {content}")
            elif role == "assistant":
                conversation_parts.append(f"Assistant: {content}")
        
        if system_content:
            return f"{system_content}\n\n{chr(10).join(conversation_parts)}"
        return chr(10).join(conversation_parts)
    
    async def _call_openai_streaming(
        self,
        messages: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """Stream OpenAI response chunks in real-time."""
        
        handler = get_streaming_handler()
        
        try:
            stream = self._client.chat.completions.create(
                model=settings.llm.openai.model,
                messages=messages,
                temperature=settings.llm.openai.temperature,
                max_tokens=settings.llm.openai.max_tokens,
                top_p=settings.llm.openai.top_p,
                frequency_penalty=settings.llm.openai.frequency_penalty,
                presence_penalty=settings.llm.openai.presence_penalty,
                stream=True,
            )
            
            async for chunk in handler.stream_chunks(stream_openai_response(stream)):
                yield chunk
            
            full_response = handler.get_full_response()
            if not full_response:
                raise LLMError("Empty streaming response from OpenAI")
                
        except asyncio.CancelledError:
            raise
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"OpenAI streaming error: {str(e)}")
    
    async def _call_gemini_streaming(
        self,
        messages: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """Stream Gemini response chunks in real-time."""
        handler = get_streaming_handler()
        
        try:
            formatted_prompt = self._format_messages_for_gemini(messages)
            response = self._client.generate_content(formatted_prompt, stream=True)
            
            async for chunk in handler.stream_chunks(stream_gemini_response(response)):
                yield chunk
            
            full_response = handler.get_full_response()
            if not full_response:
                raise LLMError("Empty streaming response from Gemini")
                
        except asyncio.CancelledError:
            raise
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"Gemini streaming error: {str(e)}")
    
    def _call_openai_with_retry(self, messages: List[Dict[str, str]]) -> str:
        max_retries = settings.llm.openai.max_retries
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                return self._call_openai(messages)
            except LLMError as e:
                last_error = str(e)
                
                if 'rate limit' in last_error.lower() and attempt < max_retries:
                    wait_time = (2 ** attempt) + (attempt * 0.5)
                    time.sleep(wait_time)
                    continue
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise
        
        raise LLMError(f"Failed after {max_retries} attempts: {last_error}")
    
    def _call_gemini_with_retry(self, messages: List[Dict[str, str]]) -> str:
        max_retries = settings.llm.gemini.max_retries
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                return self._call_gemini(messages)
            except LLMError as e:
                last_error = str(e)
                
                if 'rate limit' in last_error.lower() and attempt < max_retries:
                    wait_time = (2 ** attempt) + (attempt * 0.5)
                    time.sleep(wait_time)
                    continue
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise
        
        raise LLMError(f"Failed after {max_retries} attempts: {last_error}")
    
    async def _call_openai_with_retry_async(self, messages: List[Dict[str, str]]) -> str:
        max_retries = settings.llm.openai.max_retries
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                return self._call_openai(messages)
            except LLMError as e:
                last_error = str(e)
                
                if 'rate limit' in last_error.lower() and attempt < max_retries:
                    wait_time = (2 ** attempt) + (attempt * 0.5)
                    await asyncio.sleep(wait_time)
                    continue
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    raise
        
        raise LLMError(f"Failed after {max_retries} attempts: {last_error}")
    
    async def _call_gemini_with_retry_async(self, messages: List[Dict[str, str]]) -> str:
        max_retries = settings.llm.gemini.max_retries
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                return self._call_gemini(messages)
            except LLMError as e:
                last_error = str(e)
                
                if 'rate limit' in last_error.lower() and attempt < max_retries:
                    wait_time = (2 ** attempt) + (attempt * 0.5)
                    await asyncio.sleep(wait_time)
                    continue
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    raise
        
        raise LLMError(f"Failed after {max_retries} attempts: {last_error}")

    def generate_greeting(self, user_id: str) -> str:
        try:
            user = self.user_repo.get_by_id(user_id)
            profile = self.profile_repo.get_by_user_id(user_id)
            
            user_response = UserResponse(**user)
            profile_response = ProfileResponse(**profile) if profile else None
            
            greeting_prompt = self.prompt_builder.build_greeting_prompt(user_response, profile_response)
            
            messages = [
                {"role": "system", "content": greeting_prompt},
                {"role": "user", "content": "Hello"}
            ]
            
            if settings.llm.provider == "openai":
                return self._call_openai_with_retry(messages)
            else:
                return self._call_gemini_with_retry(messages)
            
        except Exception as e:
            raise LLMError(f"Failed to generate greeting: {str(e)}")
    
    def generate_recommendation(
        self,
        user_id: str,
        messages: List[Dict[str, str]],
        products: List[ProductResponse]
    ) -> str:
        try:
            user = self.user_repo.get_by_id(user_id)
            profile = self.profile_repo.get_by_user_id(user_id)
            
            user_response = UserResponse(**user)
            profile_response = ProfileResponse(**profile) if profile else None
            
            recommendation_prompt = self.prompt_builder.build_recommendation_prompt(
                user_response,
                profile_response,
                products
            )
            
            formatted_messages = [{"role": "system", "content": recommendation_prompt}]
            
            context_window = settings.conversation.context_window_messages
            recent_messages = messages[-context_window:] if len(messages) > context_window else messages
            formatted_messages.extend(recent_messages)
            
            if settings.llm.provider == "openai":
                return self._call_openai_with_retry(formatted_messages)
            else:
                return self._call_gemini_with_retry(formatted_messages)
            
        except Exception as e:
            raise LLMError(f"Failed to generate recommendation: {str(e)}")
    
    def generate_comparison(
        self,
        user_id: str,
        messages: List[Dict[str, str]],
        products: List[ProductResponse]
    ) -> str:
        try:
            user = self.user_repo.get_by_id(user_id)
            profile = self.profile_repo.get_by_user_id(user_id)
            
            user_response = UserResponse(**user)
            profile_response = ProfileResponse(**profile) if profile else None
            
            comparison_prompt = self.prompt_builder.build_comparison_prompt(
                user_response,
                profile_response,
                products
            )
            
            formatted_messages = [{"role": "system", "content": comparison_prompt}]
            
            context_window = settings.conversation.context_window_messages
            recent_messages = messages[-context_window:] if len(messages) > context_window else messages
            formatted_messages.extend(recent_messages)
            
            if settings.llm.provider == "openai":
                return self._call_openai_with_retry(formatted_messages)
            else:
                return self._call_gemini_with_retry(formatted_messages)
            
        except Exception as e:
            raise LLMError(f"Failed to generate comparison: {str(e)}")
    
    def analyze_intent(self, user_message: str) -> Dict[str, Any]:
        try:
            analysis_prompt = self.intent_analyzer.get_analysis_prompt()
            
            messages = [
                {"role": "system", "content": analysis_prompt},
                {"role": "user", "content": user_message}
            ]
            
            if settings.llm.provider == "openai":
                response = self._call_openai_with_retry(messages)
            else:
                response = self._call_gemini_with_retry(messages)
            
            return self.intent_analyzer.analyze(user_message, response)
            
        except Exception:
            return self.intent_analyzer._get_default_intent()
    
    def health_check(self) -> bool:
        try:
            test_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
            
            if settings.llm.provider == "openai":
                response = self._client.chat.completions.create(
                    model=settings.llm.openai.model,
                    messages=test_messages,
                    max_tokens=10
                )
                return bool(response.choices)
            else:
                formatted_prompt = self._format_messages_for_gemini(test_messages)
                response = self._client.generate_content(formatted_prompt)
                return bool(response.text)
            
        except Exception:
            return False


def get_llm_service() -> LLMService:
    return LLMService()

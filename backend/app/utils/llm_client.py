"""
LLM客户端封装
统一使用OpenAI格式调用
"""

import json
import logging
import re
from typing import Optional, Dict, Any, List
from openai import OpenAI, APIError, BadRequestError

from ..config import Config
from ..i18n import tr

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM客户端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME
        self.default_max_tokens = Config.LLM_MAX_TOKENS
        
        if not self.api_key:
            raise ValueError(tr("config.llm_key_missing"))
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    @staticmethod
    def _trim_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Trim old context while preserving the initial prompt and recent turns."""
        if len(messages) <= 8:
            return messages

        head_count = 2 if len(messages) >= 2 else 1
        tail_count = min(8, len(messages) - head_count)
        tail_start = max(head_count, len(messages) - tail_count)
        trimmed = messages[:head_count] + messages[tail_start:]

        if len(trimmed) < len(messages):
            logger.warning("Trimmed LLM context from %s to %s messages", len(messages), len(trimmed))

        return trimmed

    @staticmethod
    def _is_context_length_error(exc: Exception) -> bool:
        text = str(exc).lower()
        markers = (
            "context_length",
            "maximum context",
            "context window",
            "too many tokens",
            "maximum tokens",
            "token limit",
        )
        return any(marker in text for marker in markers)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（如JSON模式）
            
        Returns:
            模型响应文本
        """
        if max_tokens is None:
            max_tokens = self.default_max_tokens

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if response_format:
            kwargs["response_format"] = response_format

        try:
            response = self.client.chat.completions.create(**kwargs)
        except BadRequestError as exc:
            if not self._is_context_length_error(exc):
                raise

            trimmed_messages = self._trim_messages(messages)
            if len(trimmed_messages) == len(messages):
                raise

            logger.warning("Retrying LLM call after context-length failure")
            kwargs["messages"] = trimmed_messages
            response = self.client.chat.completions.create(**kwargs)
        except APIError:
            logger.exception("LLM API request failed")
            raise

        content = response.choices[0].message.content or ""
        # 部分模型会在 content 中夹带 <think>...</think>，且标签大小写不固定
        content = re.sub(r'<think\b[^>]*>[\s\S]*?</think>', '', content, flags=re.IGNORECASE).strip()
        return content

    @staticmethod
    def _extract_json_payload(response_text: str) -> str:
        """从混合文本中提取可解析的 JSON 负载。"""
        text = (response_text or "").strip().lstrip('\ufeff')

        text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\n?```\s*$', '', text)
        text = text.strip()

        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass

        decoder = json.JSONDecoder()
        for index, char in enumerate(text):
            if char not in '{[':
                continue

            try:
                _, end = decoder.raw_decode(text[index:])
                candidate = text[index:index + end].strip()
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass

        return text
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送聊天请求并返回JSON
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            解析后的JSON对象
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            # 不设置 response_format，以兼容 LM Studio / Ollama 等仅支持纯文本 JSON 输出的后端
        )
        cleaned_response = self._extract_json_payload(response)

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(tr("llm.invalid_json", payload=cleaned_response))

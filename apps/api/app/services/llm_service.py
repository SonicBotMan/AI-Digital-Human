from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

from app.core.config import Settings

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    def __init__(self, message: str, provider_error: Exception | None = None):
        super().__init__(message)
        self.provider_error = provider_error


class LLMService:
    def __init__(self, settings: Settings, vendor_configs: dict[str, Any] | None = None):
        self._settings = settings
        self._provider = settings.LLM_PROVIDER
        self._default_model = settings.DEFAULT_LLM_MODEL
        self._max_tokens = settings.MAX_TOKENS
        self._temperature = settings.TEMPERATURE
        self._vendor_configs = vendor_configs or {}

        if self._provider == "glm":
            glm_config = self._vendor_configs.get("glm", {})
            api_key = glm_config.get("api_key") or settings.GLM_API_KEY
            base_url = glm_config.get("base_url")

            if not api_key:
                raise LLMServiceError("GLM_API_KEY is required when LLM_PROVIDER=glm")
            from zhipuai import ZhipuAI

            self._client = ZhipuAI(api_key=api_key, base_url=base_url)
            self._default_model = settings.GLM_MODEL
        elif self._provider == "minimax":
            minimax_config = self._vendor_configs.get("minimax", {})
            api_key = minimax_config.get("api_key") or settings.MINIMAX_API_KEY
            if not api_key:
                raise LLMServiceError("MINIMAX_API_KEY is required when LLM_PROVIDER=minimax")
            self._client = None
            self._default_model = settings.MINIMAX_MODEL
        elif self._provider == "openai":
            openai_config = self._vendor_configs.get("openai", {})
            api_key = openai_config.get("api_key") or settings.OPENAI_API_KEY
            base_url = openai_config.get("base_url")

            if not api_key:
                raise LLMServiceError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
            import aisuite as ai

            client_config = {"api_key": api_key}
            if base_url:
                client_config["base_url"] = base_url

            self._client = ai.Client(provider_configs={"openai": client_config})
            self._default_model = settings.OPENAI_MODEL
        else:
            raise LLMServiceError(f"Unsupported LLM_PROVIDER: {self._provider}")

        logger.info("LLMService initialized — provider=%s, model=%s", self._provider, self._default_model)

    def _build_messages(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None,
    ) -> list[dict[str, str]]:
        if system_prompt is None:
            return list(messages)
        return [{"role": "system", "content": system_prompt}, *messages]

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        model: str | None = None,
    ) -> str:
        resolved_model = model or self._default_model
        full_messages = self._build_messages(messages, system_prompt)

        try:
            if self._provider == "glm":
                response = self._client.chat.completions.create(
                    model=resolved_model,
                    messages=full_messages,
                    max_tokens=self._max_tokens,
                    temperature=self._temperature,
                )
                content = response.choices[0].message.content
            elif self._provider == "minimax":
                content = self._minimax_chat(full_messages, resolved_model)
            else:
                response = self._client.chat.completions.create(
                    model=resolved_model,
                    messages=full_messages,
                    max_tokens=self._max_tokens,
                    temperature=self._temperature,
                )
                content = response.choices[0].message.content
        except Exception as exc:
            logger.exception("chat_completion failed — model=%s", resolved_model)
            raise LLMServiceError(f"LLM request failed: {exc}", provider_error=exc) from exc

        return content or ""

    def _minimax_chat(self, messages: list[dict], model: str) -> str:
        import httpx

        url = f"https://api.minimax.chat/v1/text/chatcompletion_pro?GroupId={self._settings.MINIMAX_GROUP_ID}"
        headers = {"Authorization": f"Bearer {self._settings.MINIMAX_API_KEY}"}
        payload = {
            "model": model,
            "messages": messages,
            "tokens_to_generate": self._max_tokens,
            "temperature": self._temperature,
        }
        resp = httpx.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()["reply"]

    async def stream_chat_completion(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        model: str | None = None,
    ) -> AsyncIterator[str]:
        import asyncio

        resolved_model = model or self._default_model
        full_messages = self._build_messages(messages, system_prompt)

        def _sync_stream():
            if self._provider == "glm":
                stream = self._client.chat.completions.create(
                    model=resolved_model,
                    messages=full_messages,
                    max_tokens=self._max_tokens,
                    temperature=self._temperature,
                    stream=True,
                )
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            elif self._provider == "minimax":
                content = self._minimax_chat(full_messages, resolved_model)
                yield content
            else:
                stream = self._client.chat.completions.create(
                    model=resolved_model,
                    messages=full_messages,
                    max_tokens=self._max_tokens,
                    temperature=self._temperature,
                    stream=True,
                )
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

        try:
            loop = asyncio.get_running_loop()
            for chunk in await asyncio.to_thread(lambda: list(_sync_stream())):
                yield chunk
        except RuntimeError:
            for chunk in _sync_stream():
                yield chunk
        except Exception as exc:
            logger.exception("stream_chat_completion failed — model=%s", resolved_model)
            raise LLMServiceError(f"LLM stream request failed: {exc}", provider_error=exc) from exc

    def count_tokens(self, text: str) -> int:
        try:
            import tiktoken

            encoding = tiktoken.encoding_for_model(self._default_model.replace("openai:", ""))
        except (ImportError, KeyError):
            logger.debug("tiktoken unavailable or model unsupported — using heuristic")
            return max(1, len(text) // 4)

        return len(encoding.encode(text))

    def embed_text(self, text: str) -> list[float]:
        if self._provider == "glm":
            return self._glm_embed(text)
        elif self._provider == "minimax":
            return self._minimax_embed(text)
        else:
            return self._openai_embed(text)

    def _glm_embed(self, text: str) -> list[float]:
        response = self._client.embeddings.create(
            model="embedding-2",
            input=text,
        )
        return response.data[0].embedding

    def _minimax_embed(self, text: str) -> list[float]:
        import httpx

        url = f"https://api.minimax.chat/v1/embeddings?GroupId={self._settings.MINIMAX_GROUP_ID}"
        headers = {"Authorization": f"Bearer {self._settings.MINIMAX_API_KEY}"}
        payload = {"model": "MiniMax-Embedding-01", "texts": [text]}
        resp = httpx.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()["vectors"][0]

    def _openai_embed(self, text: str) -> list[float]:
        import openai

        client = openai.OpenAI(api_key=self._settings.OPENAI_API_KEY)
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small",
        )
        return response.data[0].embedding

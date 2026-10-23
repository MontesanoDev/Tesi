"""Embedding services, independent of the generative model and vector store."""

from typing import Literal

EmbeddingProvider = Literal["ollama", "openai", "mistral", "compatible"]

EMBEDDING_PROVIDERS = (
    {"id": "ollama", "name": "Ollama", "base_url": "http://127.0.0.1:11434",
     "default_model": "bge-m3", "requires_key": False},
    {"id": "openai", "name": "OpenAI", "base_url": "https://api.openai.com/v1",
     "default_model": "text-embedding-3-small", "requires_key": True},
    {"id": "mistral", "name": "Mistral", "base_url": "https://api.mistral.ai/v1",
     "default_model": "mistral-embed", "requires_key": True},
    {"id": "compatible", "name": "Compatibile con OpenAI", "base_url": "",
     "default_model": "", "requires_key": False},
)

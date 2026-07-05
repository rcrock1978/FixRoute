"""Embedding service — text (OpenAI ada-002, 1536-d) + image (CLIP, 512-d).

Per the duplicate-detection spec: combines text + image embeddings for cosine
similarity search. The MVP uses a deterministic hash-based stub for tests;
production routes through Azure OpenAI embeddings + CLIP via LangChain.
"""
from __future__ import annotations

import hashlib
import os
from typing import Protocol


class EmbedderPort(Protocol):
    def embed_text(self, text: str) -> list[float]: ...
    def embed_image(self, image_bytes: bytes) -> list[float]: ...


def _hash_embed(text: str, dim: int) -> list[float]:
    """Deterministic stub: hashes text → unit-normalized float vector of `dim` dims."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    raw = [b / 255.0 for b in digest] * (dim // len(digest) + 1)
    vector = raw[:dim]
    norm = sum(x * x for x in vector) ** 0.5 or 1.0
    return [x / norm for x in vector]


class HashEmbedder:
    """Stub embedder for tests + dev. Deterministic, no external API."""

    def embed_text(self, text: str) -> list[float]:
        return _hash_embed(text, dim=1536)

    def embed_image(self, image_bytes: bytes) -> list[float]:
        return _hash_embed(image_bytes.hex(), dim=512)


class LangChainEmbedder:
    """Production embedder — routes through Azure OpenAI + CLIP via LangChain."""

    def embed_text(self, text: str) -> list[float]:
        from langchain_openai import AzureOpenAIEmbeddings

        client = AzureOpenAIEmbeddings(model="text-embedding-ada-002")
        return client.embed_query(text)

    def embed_image(self, image_bytes: bytes) -> list[float]:
        from langchain.embeddings import OpenCLIPEmbeddings

        client = OpenCLIPEmbeddings()
        return client.embed_image(image_bytes)


def get_embedder() -> EmbedderPort:
    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        return LangChainEmbedder()
    return HashEmbedder()

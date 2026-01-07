import tempfile
import requests
from typing import Tuple


class ContentResolver:
    """
    Resolves content into a usable form for the pipeline.

    Returns:
        mode: 'text' or 'video'
        payload: raw text OR local file path
    """

    def resolve(self, content_type: str, content_source: dict) -> Tuple[str, str]:
        source_type = content_source.get("type")

        # ----------------------------
        # Inline text
        # ----------------------------
        if source_type == "inline":
            return "text", content_source["text"]

        # ----------------------------
        # Local file (for POC/testing)
        # ----------------------------
        if source_type == "local":
            return content_type, content_source["path"]

        # ----------------------------
        # Remote URI (Azure Blob, etc.)
        # ----------------------------
        if source_type == "uri":
            return self._resolve_uri(content_type, content_source)

        raise ValueError(f"Unsupported content source type: {source_type}")

    def _resolve_uri(self, content_type: str, content_source: dict) -> Tuple[str, str]:
        headers = {}

        auth = content_source.get("auth")
        if auth and auth.get("type") == "bearer":
            headers["Authorization"] = f"Bearer {auth['token']}"

        response = requests.get(
            content_source["uri"],
            headers=headers,
            stream=True,
            timeout=60,
        )
        response.raise_for_status()

        # ----------------------------
        # Text content
        # ----------------------------
        if content_type == "text":
            return "text", response.text

        # ----------------------------
        # Video content
        # ----------------------------
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        for chunk in response.iter_content(chunk_size=8192):
            tmp.write(chunk)
        tmp.close()

        return "video", tmp.name

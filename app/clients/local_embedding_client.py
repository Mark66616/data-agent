from huggingface_hub import AsyncInferenceClient, InferenceClient


class LocalEmbeddingClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.embed_url = self._build_embed_url(self.base_url)
        self.client = InferenceClient(base_url=self.embed_url)
        self.async_client = AsyncInferenceClient(base_url=self.embed_url)

    @staticmethod
    def _build_embed_url(base_url: str) -> str:
        if base_url.endswith("/embed"):
            return base_url
        return f"{base_url}/embed"

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        texts = [text.replace("\n", " ") for text in texts]
        response = self.client.feature_extraction(text=texts)
        return response.tolist()

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        texts = [text.replace("\n", " ") for text in texts]
        response = await self.async_client.feature_extraction(text=texts)
        return response.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    async def aembed_query(self, text: str) -> list[float]:
        return (await self.aembed_documents([text]))[0]

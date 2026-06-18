from typing import Optional

from app.conf.app_config import EmbeddingConfig, app_config
from app.clients.local_embedding_client import LocalEmbeddingClient


class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.client: Optional[LocalEmbeddingClient] = None
        self.config = config

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = LocalEmbeddingClient(base_url=self._get_url())

# 需要注意的是，huggingface提供的接口不分同步异步，如果使用异步直接使用a开头的方法即可
# 比如：embed_query(text) embed_document([text]) aembed_query(text) aembed_document([text])
embedding_client_manager = EmbeddingClientManager(app_config.embedding)

from typing import Optional

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.client: Optional[HuggingFaceEndpointEmbeddings] = None
        self.config = config

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = HuggingFaceEndpointEmbeddings(model=self._get_url())

# 需要注意的是，huggingface提供的接口不分同步异步，如果使用异步直接使用a开头的方法即可
# 比如：embed_query(text) embed_document([text]) aembed_query(text) aembed_document([text])
embedding_client_manager = EmbeddingClientManager(app_config.embedding)

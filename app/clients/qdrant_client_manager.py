from typing import Optional

from qdrant_client import AsyncQdrantClient

from app.conf.app_config import QdrantConfig, app_config

class QdrantClientManager:
    def __init__(self, qdrant_config: QdrantConfig):
        self.qdrant_config = qdrant_config
        self.client: Optional[AsyncQdrantClient] = None

    def _get_url(self):
        return f"http://{self.qdrant_config.host}:{self.qdrant_config.port}"

    def init(self):
        # 初始化QdrantClient，fastapi启动时调用
        self.client = AsyncQdrantClient(url=self._get_url())

    async def close(self):
        # 关闭QdrantClient，fastapi关闭时调用
        await self.client.close()

# python会把每个文件当成一个模块，所以这里需要初始化一个QdrantClientManager对象，并且是一个全局单里对象
qdrant_client_manager = QdrantClientManager(app_config.qdrant)
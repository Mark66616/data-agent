from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.models import Distance
from qdrant_client.models import VectorsConfig

from app.conf.app_config import app_config


class ColumnQdrantRepository:
    collection_name = "data_agent_column_info"

    def __init__(self, qdrant_client: AsyncQdrantClient):
        self.qdrant_client: AsyncQdrantClient = qdrant_client

    async def ensure_collection(self):
        """
        确保集合存在
        """
        if not await self.qdrant_client.collection_exists(self.collection_name):
            await self.qdrant_client.create_collection(collection_name=self.collection_name
                                                       , vectors_config=VectorsConfig(
                    size=app_config.qdrant.embedding_size
                    , distance=Distance.COSINE))

    async def upsert(self, ids: list[str], embeddings: list[list[float]], payloads: list[dict], batch_size: int = 10):
        """
        批量保存向量
        :param ids: 向量唯一id
        :param embeddings: 向量
        :param payloads: 元数据
        :param batch_size: 保存向量数据库的批次
        :return:
        """
        # 包装qdrant所需要的向量存储结构
        vector_points = [PointStruct(id=id, vector=embedding, payload=payload) for id, embedding, payload in
                         zip(ids, embeddings, payloads)]
        # 批量保存向量
        for i in range(0, len(vector_points), batch_size):
            await self.qdrant_client.upsert(collection_name=self.collection_name,
                                            points=vector_points[i:i + batch_size])

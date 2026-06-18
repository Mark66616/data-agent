from dataclasses import asdict

from elasticsearch import AsyncElasticsearch

from app.models.value_info import ValueInfo


class ValueEsRepository:
    value_index_name = "data_agent_value_index"
    index_mappings = {
        "dynamic": False,
        "properties": {
            "id": {"type": "keyword"},
            "value": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_max_word"},
            "column_id": {"type": "keyword"}
        }
    }

    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client: AsyncElasticsearch = es_client

    async def ensure_index(self):
        if not await self.es_client.exists(index=self.value_index_name):
            await self.es_client.indices.create(index=self.value_index_name,
                                                mappings=self.index_mappings)

    async def batch_bulk_value_infos(self, target_value_infos: list[ValueInfo], batch_size=10):
        operations: list[dict] = []
        for i in range(0, len(target_value_infos), batch_size):
            batch_value_infos = target_value_infos[i:i + batch_size]
            for value_info in batch_value_infos:
                operations.append({
                    "index": {
                        "_index": self.value_index_name
                    }
                })
                operations.append(asdict(value_info))
        # 批量插入
        for i in range(0, len(operations), batch_size):
            batch_operations = operations[i:i + batch_size]
            await self.es_client.bulk(operations=batch_operations)

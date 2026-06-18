import uuid
from pathlib import Path

from omegaconf import OmegaConf

from app.clients.local_embedding_client import LocalEmbeddingClient
from app.conf.meta_config import MetaConfig
from app.core.log import logger
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.models.value_info import ValueInfo
from app.reposities.es.value_es_repository import ValueEsRepository
from app.reposities.mysql.dw.dw_mysql_repository import DwMsqlRepository
from app.reposities.mysql.meta.meta_sql_repository import MetaSqlRepository
from app.reposities.qdrant.column_qdrant_repository import ColumnQdrantRepository


class MateKnowledgeService:
    def __init__(self, meta_sql_repository: MetaSqlRepository
                 , dw_sql_repository: DwMsqlRepository
                 , column_qdrant_repository: ColumnQdrantRepository
                 , embedding_client: LocalEmbeddingClient
                 , value_es_repository: ValueEsRepository
                 ):
        self.column_qdrant_repository = column_qdrant_repository
        self.meta_sql_repository: MetaSqlRepository = meta_sql_repository
        self.dw_sql_repository: DwMsqlRepository = dw_sql_repository
        self.embedding_client: LocalEmbeddingClient = embedding_client
        self.value_es_repository = value_es_repository

    async def build(self, config_path: Path):
        logger.info(f"读取元知识库配置文件: {config_path}")
        # 1 读取yaml
        conf = OmegaConf.load(config_path)
        # 1.1 定义实体类结构
        schema = OmegaConf.structured(MetaConfig)
        # 1.2 将配置文件绑定实体类结构
        # merge中要先放schema，再放conf，否则会取schema中的默认参数None
        omega_config = OmegaConf.merge(schema, conf)
        # 1.3:加载yaml并赋值给实体类
        meta_config: MetaConfig = OmegaConf.to_object(omega_config)

        # 2 根据配置文件同步指定的元数据库和向量索引以及全文索引
        if meta_config.tables:
            table_infos: list[TableInfo] = []
            column_infos: list[ColumnInfo] = []

            for table in meta_config.tables:
                table_info = TableInfo(id=table.name, name=table.name, role=table.role,
                                       description=table.description)
                table_infos.append(table_info)

                # 查询表结构字段类型
                column_types = await self.dw_sql_repository.get_table_columns(table.name)

                for column in table.columns:
                    # 查询字段取值示例
                    column_examples = await self.dw_sql_repository.get_column_examples(table.name, column.name)

                    column_info = ColumnInfo(id=f"{table.name}.{column.name}", name=column.name,
                                             type=column_types[column.name], role=column.role,
                                             examples=column_examples, description=column.description,
                                             alias=column.alias, table_id=table.name)
                    column_infos.append(column_info)

            # 保存表结构，使用自动提交事物，有异常自动会滚
            async with self.meta_sql_repository.session.begin():
                await self.meta_sql_repository.save_table_infos(table_infos)
                await self.meta_sql_repository.save_column_infos(column_infos)

            # 3 将关键字段信息进行向量化并存储到数据库
            await self.column_qdrant_repository.ensure_collection()

            # 3.1 构建向量数据的元数据
            points: list[dict] = []
            for column_info in column_infos:
                # 字段表的name转为一个向量
                points.append({
                    "id": uuid.uuid4(),
                    "embedding_text": column_info.name,
                    "payload": column_info
                })
                # 字段表的description转为一个向量
                points.append({
                    "id": uuid.uuid4(),
                    "embedding_text": column_info.description,
                    "payload": column_info
                })
                # 字段表的alias中的每一个元素转为一个向量
                for alias in column_info.alias:
                    points.append({
                        "id": uuid.uuid4(),
                        "embedding_text": alias,
                        "payload": column_info
                    })

                # 分批次进行向量化并保存
                batch_points_size = 5
                # 分批次地将embedding_text进行向量化
                embeddings: list[list[float]] = []
                for i in range(0, len(points), batch_points_size):
                    batch_points = [point["embedding_text"] for point in points[i:i + batch_points_size]]
                    embeds = await self.embedding_client.aembed_documents(batch_points)
                    # extend将列表中的元素展开放入一个列表中(append是将放入的源数据直接当作目标列表的元素放入)
                    embeddings.extend(embeds)

                # 分批次将向量化结果保存到数据库
                ids = [point["id"] for point in points]
                payloads = [point["payload"] for point in points]

                await self.column_qdrant_repository.upsert(ids, embeddings, payloads)

            # 4 对维度字段信息创建全文索引并保存在es中
            await self.value_es_repository.ensure_index()

            target_value_infos: list[ValueInfo] = []
            for table_info in meta_config.tables:
                for column_info in table_info.columns:
                    if column_info.sync:
                        # 收集需要创建全文索引的值
                        current_value_infos = await self.dw_sql_repository.get_column_examples(table_info.name,
                                                                                               column_info.name,
                                                                                               limit=9999999)
                        value_infos = [ValueInfo(id=f"{table_info.name}.{column_info.name}.{current_value_info}",
                                                 value=current_value_info,
                                                 column_id=f"{table_info.name}.{column_info.name}"
                                                 ) for current_value_info in current_value_infos]
                        target_value_infos.extend(value_infos)

            # 分批保存创建全文索引
            await self.value_es_repository.batch_bulk_value_infos(target_value_infos)

        if meta_config.metrics:
            for metrics in meta_config.metrics:
                # 将指标信息同步到meta数据库中

                # 将指标信息进行向量化并存储到数据库
                print(metrics)

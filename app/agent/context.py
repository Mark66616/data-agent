from typing import TypedDict

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.reposities.es.value_es_repository import ValueEsRepository
from app.reposities.mysql.dw.dw_mysql_repository import DwMsqlRepository
from app.reposities.mysql.meta.meta_sql_repository import MetaMySqlRepository
from app.reposities.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.reposities.qdrant.metric_qdrant_repository import MetricQdrantRepository


class DataAgentContext(TypedDict):
    embedding_client: HuggingFaceEndpointEmbeddings
    column_qdrant_repository: ColumnQdrantRepository
    metric_qdrant_repository: MetricQdrantRepository
    value_es_repository: ValueEsRepository
    meta_sql_repository: MetaMySqlRepository
    dw_sql_repository: DwMsqlRepository

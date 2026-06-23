from typing import TypedDict

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.reposities.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.reposities.qdrant.metric_qdrant_repository import MetricQdrantRepository


class DataAgentContext(TypedDict):
    embedding_client: HuggingFaceEndpointEmbeddings
    column_qdrant_repository: ColumnQdrantRepository
    metric_qdrant_repository: MetricQdrantRepository

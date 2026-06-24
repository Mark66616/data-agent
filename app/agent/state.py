from dataclasses import dataclass
from typing import TypedDict

from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.models.value_info import ValueInfo


@dataclass
class TableColumnState(TypedDict):
    name: str
    type: str
    description: str
    role:str
    examples: list[str]
    alias: list[str]

@dataclass
class TableInfoState(TypedDict):
    name:str
    role:str
    description:str
    columns: list[TableColumnState]

@dataclass
class MetricInfoState(TypedDict):
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]

@dataclass
class CurrentDateState(TypedDict):
    year: int
    month: int
    day: int
    date: str
    week_day:str
    quarter: str

@dataclass
class DbInfoState(TypedDict):
    # 数据库方言（具体数据库名，比如：mysql、redis、qdrant...）
    dialect: str
    # 数据库版本
    version: str

class DataAgentState(TypedDict):
    # 用户查询
    user_query: str

    # 用户查询抽取的关键词
    keywords: str

    # 召回的列信息
    recall_columns: list[ColumnInfo]
    # 召回的指标信息
    recall_metrics: list[MetricInfo]
    # 召回的值信息
    recall_values: list[ValueInfo]

    # 合并的表信息
    merge_table_infos: list[TableInfoState]
    # 合并的指标信息
    merge_metric_infos: list[MetricInfoState]

    # 过滤后的表信息
    filter_table_infos: list[TableInfoState]
    # 过滤后的指标信息
    filter_metric_infos: list[MetricInfoState]

    # 添加额外的上下文
    # 当前年月日季度
    current_date: CurrentDateState
    # 数据库信息
    db_info: DbInfoState

    # 生成和校正的SQL
    generated_sql: str

    # 校验SQL时出现的错误信息
    error: str

    # sql执行结果
    sql_result: list[dict]
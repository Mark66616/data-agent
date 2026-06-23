from typing import TypedDict


class DataAgentState(TypedDict):
    # 用户查询
    user_query: str

    # 用户查询抽取的关键词
    keywords: str

    # 召回的列信息
    recall_columns: list[dict]

    # 召回的指标信息
    recall_metrics: list[dict]

    # 校验SQL时出现的错误信息
    error: str

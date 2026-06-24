from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, TableInfoState, TableColumnState, MetricInfoState
from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.models.value_info import ValueInfo


async def merge_recall_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "合并召回信息", "status": "running"})

    # 用户查询
    user_query = state["user_query"]
    # 获取已召回的信息
    recall_columns: list[ColumnInfo] = state["recall_columns"]
    recall_metrics: list[MetricInfo] = state["recall_metrics"]
    recall_values: list[ValueInfo] = state["recall_values"]

    meta_sql_repository = runtime.context["meta_sql_repository"]

    # 处理表信息
    recall_column_map: dict[str, ColumnInfo] = {column.id: column for column in recall_columns}

    # 将指标信息的相关字段添加到字段信息中
    for recall_metric in recall_metrics:
        for column_id in recall_metric.relevant_columns:
            if column_id not in recall_column_map:
                column_info: ColumnInfo = await meta_sql_repository.get_column_info_by_id(column_id)
                recall_column_map[column_id] = column_info

    # 将值信息的相关信息放入examples中
    for recall_value in recall_values:
        value = recall_value.value
        column_id = recall_value.id
        if column_id not in recall_column_map:
            column_info: ColumnInfo = await meta_sql_repository.get_column_info_by_id(column_id)
            recall_column_map[column_id] = column_info

        if value not in recall_column_map[column_id].examples:
            recall_column_map[column_id].examples.append(value)

    # 按照表对字段信息进行分组，整理为目标格式
    table_to_column_map: dict[str, list[ColumnInfo]] = {}
    for column in recall_column_map.values():
        table_id = column.table_id
        if table_id not in table_to_column_map:
            table_to_column_map[table_id] = []
        table_to_column_map[table_id].append(column)

    table_infos: list[TableInfoState] = []
    for table_id, columns in table_to_column_map.items():
        # 根据table——id查询表信息
        table_info: TableInfo = await meta_sql_repository.get_table_info_by_id(table_id)
        if table_info is None:
            continue

        column_info_states = [TableColumnState(
            name=column.name,
            description=column.description,
            type=column.type,
            examples=column.examples,
            role=column.role,
            alias=column.alias
        ) for column in columns]

        table_info_state = TableInfoState(
            name=table_id,
            description=table_info.description,
            role=table_info.role,
            columns=column_info_states
        )

        table_infos.append(table_info_state)

    # 处理指标信息
    metric_info_states = [MetricInfoState(
        name=metric.name,
        description=metric.description,
        alias=metric.alias,
        relevant_columns=metric.relevant_columns
    ) for metric in recall_metrics]

    return {
        "table_infos": table_infos,
        "metric_infos": metric_info_states
    }

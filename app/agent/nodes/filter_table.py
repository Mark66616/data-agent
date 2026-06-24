import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, TableInfoState, TableColumnState
from app.core.log import logger
from app.prompt.propmpt_loader import load_prompt


async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "过滤表信息", "status": "running"})

    # 用户查询
    user_query = state["user_query"]
    # 获取已经合并的表信息
    merge_table_infos: list[TableInfoState] = state["merge_table_infos"]

    try:
        prompt = PromptTemplate(
            template=load_prompt("filter_table_info"),
            input_variables=["user_query", "table_infos"],
        )

        output_parser = JsonOutputParser()

        chain = prompt | llm | output_parser

        # 调用大模型
        # result约定的格式为：
        # {
        #   "表名1":[字段名1，字段名2...],
        #   "表名2":[字段名1，字段名2...],
        # }
        result = await chain.ainvoke({"user_query": user_query,
                                      "table_infos": yaml.dump(merge_table_infos, allow_unicode=True, sort_keys=False)})

        # 剔除不在大模型认定的表结构中的字段
        for table_info in merge_table_infos:
            table_name: str = table_info['name']
            columns: list[TableColumnState] = table_info['columns']

            if table_name not in result:
                # 剔除不存在的表信息
                merge_table_infos.remove(table_info)
            else:
                # 剔除不存在的字段信息
                for column in columns:
                    column_name: str = column['name']
                    if column_name not in result[table_name]:
                        columns.remove(column)

        writer({"type": "progress", "step": "过滤表信息", "status": "success"})
        logger.info(f"过滤表信息 - 过滤后的表信息：{merge_table_infos}")

        return {"filter_table_infos": merge_table_infos}

    except Exception as e:
        writer({"type": "progress", "step": "过滤表信息", "status": "error"})
        logger.error(f"过滤表信息 - 过滤失败：{str(e)}")
        raise

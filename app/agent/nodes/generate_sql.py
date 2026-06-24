import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.propmpt_loader import load_prompt


async def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "生成SQL", "status": "running"})

    # 用户查询
    user_query = state["user_query"]

    # 获取召回并过滤后的表信息和字段信息、数据库信息、当前时间信息
    filter_table_infos = state["filter_table_infos"]
    filter_metric_infos = state["filter_metric_infos"]
    db_info = state["db_info"]
    current_date = state["current_date"]

    try:
        # 调用大模型
        prompt = PromptTemplate(
            template=load_prompt("generate_sql"),
            input_variables=["user_query", "filter_table_infos", "filter_metric_infos", "db_info", "current_date"]
        )

        output_parser = JsonOutputParser()

        chain = prompt | llm | output_parser

        sql = await chain.ainvoke(input={"user_query": user_query,
                                         "filter_table_infos": yaml.dump(filter_table_infos, allow_unicode=True,
                                                                         sort_keys=False),
                                         "filter_metric_infos": yaml.dump(filter_metric_infos, allow_unicode=True,
                                                                          sort_keys=False),
                                         "db_info": yaml.dump(db_info, allow_unicode=True, sort_keys=False),
                                         "current_date": yaml.dump(current_date, allow_unicode=True, sort_keys=False)
                                         })

        writer({"type": "progress", "step": "生成SQL", "status": "success"})
        logger.info(f"生成SQL - 成功：{sql}")

        return {"generate_sql": sql}

    except Exception as e:
        writer({"type": "progress", "step": "生成SQL", "status": "error"})
        logger.error(f"生成SQL - 发生异常：{str(e)}")
        raise

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.models.value_info import ValueInfo
from app.prompt.propmpt_loader import load_prompt


async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回值信息", "status": "running"})

    # 用户查询
    user_query = state["user_query"]
    # 获取上步结果
    keywords = state["keywords"]

    # 获取注入的客户端
    value_es_repository = runtime.context["value_es_repository"]

    try:
        # 使用大模型扩展关键字
        prompt = PromptTemplate(
            template=load_prompt("extend_keywords_for_value_recall"),
            input_variables=["user_query", "keywords"],
        )

        output_parser = JsonOutputParser()

        chain = prompt | llm | output_parser

        # 调用大模型
        result = await chain.ainvoke({"user_query": user_query})

        # 合并去重关键字
        keywords = list(set(keywords + result))
        logger.info(f"召回值信息 - 扩展后的关键字: {keywords}")

        values_map: dict[str, ValueInfo] = {}

        for keyword in keywords:
            values: list[ValueInfo] = await value_es_repository.search_value(keyword)
            for value in values:
                value_id = value.id
                if value_id in values_map:
                    values_map[value_id] = value

        recall_values = list(values_map.values())

        writer({"type": "progress", "step": "召回值信息", "status": "success"})
        logger.info(f"召回值信息 - 召回成功的值：{recall_values}")

        return {"recall_values": recall_values}

    except Exception as e:
        writer({"type": "progress", "step": "召回值信息", "status": "error"})
        logger.error(f"召回值信息 - 召回失败：{str(e)}")
        raise

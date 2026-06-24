import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, MetricInfoState
from app.core.log import logger
from app.prompt.propmpt_loader import load_prompt


async def filter_metric(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "过滤指标信息", "status": "running"})

    # 用户查询
    user_query = state["user_query"]
    # 获取已经合并的指标信息
    merge_metric_infos: list[MetricInfoState] = state["merge_metric_infos"]

    try:
        prompt = PromptTemplate(
            template=load_prompt("filter_metric_info"),
            input_variables=["user_query", "metric_infos"],
        )

        output_parser = JsonOutputParser()

        chain = prompt | llm | output_parser

        # 调用大模型认定只指标信息
        # result约定的格式为：[字段1，字段2...]
        result = await chain.ainvoke({"user_query": user_query,
                                      "metric_infos": yaml.dump(merge_metric_infos, allow_unicode=True, sort_keys=False)})

        # 剔除不在大模型认定的表结构中的字段
        for metric_info in merge_metric_infos:
            metric_name: str = metric_info['name']
            if metric_name not in result:
                # 剔除不存在的表信息
                merge_metric_infos.remove(metric_info)

        writer({"type": "progress", "step": "过滤指标信息", "status": "success"})
        logger.info(f"过滤指标信息 - 过滤后的指标信息：{merge_metric_infos}")

        return {"filter_metric_infos": merge_metric_infos}

    except Exception as e:
        writer({"type": "progress", "step": "过滤指标信息", "status": "error"})
        logger.error(f"过滤指标信息 - 获取模板失败：{str(e)}")
        raise
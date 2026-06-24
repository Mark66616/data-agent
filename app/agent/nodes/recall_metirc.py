from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.entities.metric_info import MetricInfo
from app.prompt.propmpt_loader import load_prompt


async def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回指标信息", "status": "running"})

    # 用户查询
    user_query = state["user_query"]
    # 获取上一步骤中抽取的关键字
    keywords = state["keywords"]

    # 获取注入的客户端
    embedding_client = runtime.context["embedding_client"]
    metric_qdrant_repository = runtime.context["metric_qdrant_repository"]

    try:
        # 使用大模型扩展关键字
        prompt = PromptTemplate(
            template=load_prompt("extend_keywords_for_metric_recall"),
            input_variables=["user_query"],
        )

        output_parser = JsonOutputParser()

        chain = prompt | llm | output_parser

        # 调用大模型
        result = await chain.ainvoke({"user_query": user_query})

        # 合并去重关键字
        keywords = list(set(keywords + result))
        logger.info(f"召回指标信息 - 扩展后的关键字: {keywords}")

        recall_metric_map: dict[str, MetricInfo] = {}

        for keyword in keywords:
            # 向量化关键词
            embedding = await embedding_client.aembed_query(keyword)
            # 使用关键词向量在Qdrant中检索
            payloads: list[MetricInfo] = await metric_qdrant_repository.search(embedding)

            for payload in payloads:
                metric_id = payload.id
                if metric_id not in recall_metric_map:
                    recall_metric_map[metric_id] = payload

            recall_metrics = list(recall_metric_map.values())

            writer({"type": "progress", "step": "召回指标信息", "status": "success"})
            logger.info(f"召回指标信息 - 召回成功的指标: {recall_metrics}")
            return {"recall_metrics": recall_metrics}

    except Exception as e:
        writer({"type": "progress", "step": "召回指标信息", "status": "error"})
        logger.error(f"召回指标信息 - 出现异常：{str(e)}")
        raise

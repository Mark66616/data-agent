from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def merge_recall_info(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "合并召回信息", "status": "running"})

    # 用户查询
    user_query = state["user_query"]
    # 获取已召回的信息
    recall_columns = state["recall_columns"]
    recall_metrics = state["recall_metrics"]
    recall_values = state["recall_values"]


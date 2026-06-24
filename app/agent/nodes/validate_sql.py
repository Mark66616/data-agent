from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def validate_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "校验SQL", "status": "running"})

    generated_sql = state["generated_sql"]
    dw_mysql_repository = runtime.context["dw_sql_repository"]

    try:
        await dw_mysql_repository.validate_sql(generated_sql)
        writer({"type": "progress", "step": "校验SQL", "status": "success"})
        logger.info(f"校验SQL - 成功")
        return {"error": None}
    except Exception as e:
        writer({"type": "progress", "step": "校验SQL", "status": "error"})
        logger.error(f"校验SQL - 发生异常：{str(e)}")
        return {"error": str(e)}
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def execute_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "执行SQL", "status": "running"})

    generated_sql = state["generated_sql"]
    dw_mysql_repository = runtime.context["dw_sql_repository"]

    try:
        result:list[dict] = await dw_mysql_repository.execute_sql(generated_sql)

        writer({"type": "progress", "step": "执行SQL", "status": "success"})
        logger.info(f"执行SQL - 获取结果：{result}")

        return {"sql_result": result}
    except Exception as e:
        writer({"type": "progress", "step": "执行SQL", "status": "error"})
        logger.error(f"执行SQL - 发生异常：{str(e)}")
        raise
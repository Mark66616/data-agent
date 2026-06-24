from datetime import datetime

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, CurrentDateState
from app.core.log import logger


async def add_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "添加上下文", "status": "running"})

    # 获取注入的客户端组件
    dw_mysql_repository = runtime.context["dw_sql_repository"]

    try:
        # 当前时间信息
        today = datetime.today()
        # 当前日期
        date = today.strftime("%Y-%m-%d")
        # 当前星期
        weekday = today.strftime("%A")
        # 当前季度
        quarter = today.strftime("%Q")
        current_date_info = CurrentDateState(
            year=today.year,
            month=today.month,
            day=today.day,
            date=date,
            week_day=weekday,
            quarter=quarter
        )

        # 获取数据仓库的环境信息
        db_info = await dw_mysql_repository.get_db_info()

        writer({"type": "progress", "step": "添加上下文", "status": "success"})
        logger.info(f"添加上下文 - 数据库信息：{db_info}，当前日期信息：{current_date_info}")

        return {
            "db_info": db_info,
            "current_date": current_date_info
        }

    except Exception as e:
        writer({"type": "progress", "step": "添加上下文", "status": "error"})
        logger.error(f"添加上下文 - 发生异常：{str(e)}")
        raise

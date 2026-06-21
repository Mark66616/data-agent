from typing import TypedDict


class DataAgentState(TypedDict):
    # 用户查询
    user_query:str

    # 校验SQL时出现的错误信息
    error:str
from typing import TypedDict


class DataAgentState(TypedDict):
    error:str # 校验SQL时出现的错误信息
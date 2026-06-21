import jieba.analyse
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def extract_keyword(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer("抽取关键字")

    # 用户查询
    user_query = state["user_query"]

    # 定义关键词抽取器jieba所需要的词性
    allow_pos = (
        "n",  # 名词: 数据、服务器、表格
        "nr",  # 人名: 张三、李四
        "ns",  # 地名: 北京、上海
        "nt",  # 机构团体名: 政府、学校、某公司
        "nz",  # 其他专有名词: Unicode、哈希算法、诺贝尔奖
        "v",  # 动词: 运行、开发
        "vn",  # 名动词: 工作、研究
        "a",  # 形容词: 美丽、快速
        "an",  # 名形词: 难度、合法性、复杂度
        "eng",  # 英文
        "i",  # 成语
        "l",  # 常用固定短语
    )

    # 使用jieba抽取关键词
    keywords = jieba.analyse.extract_tags(user_query, allowPOS=allow_pos)

    # 去重并添加用户查询
    # 抽取关键字并将用户原始查询添加到关键词列表中
    # 去重是因为用户查询可能很短，抽取的关键词等于用户查询
    keywords = list(set(keywords + [user_query]))

    logger.info(f"抽取的关键字: {keywords}")
    writer(f"抽取的关键字: {keywords}")
    return {"keywords": keywords}

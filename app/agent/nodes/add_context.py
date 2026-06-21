from langgraph.runtime import Runtime

from app.agent.state import DataAgentState


async def add_context(state:DataAgentState,runtime:Runtime[DataAgentState]):
    writer = runtime.stream_writer
    writer("添加额外上下文")
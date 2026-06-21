from langgraph.runtime import Runtime

from app.agent.state import DataAgentState


async def corrected_sql(state:DataAgentState,runtime:Runtime[DataAgentState]):
    writer = runtime.stream_writer
    writer("校正SQL")
    return {'error':None}
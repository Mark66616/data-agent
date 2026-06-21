from langgraph.constants import START, END
from langgraph.graph import StateGraph

from app.agent.context import DataAgentContext
from app.agent.nodes.add_context import add_context
from app.agent.nodes.corrected_sql import corrected_sql
from app.agent.nodes.execute_sql import execute_sql
from app.agent.nodes.extract_keyword import extract_keyword
from app.agent.nodes.filter_metric import filter_metric
from app.agent.nodes.filter_table import filter_table
from app.agent.nodes.generate_sql import generate_sql
from app.agent.nodes.recall_column import recall_column
from app.agent.nodes.recall_metirc import recall_metric
from app.agent.nodes.recall_value import recall_value
from app.agent.nodes.merge_recall_info import merge_recall_info
from app.agent.nodes.validate_sql import validate_sql
from app.agent.state import DataAgentState

graph_builder = StateGraph(state_schema=DataAgentState,context_schema=DataAgentContext)
graph_builder.add_node("extract_keyword",extract_keyword)
graph_builder.add_node("recall_column",recall_column)
graph_builder.add_node("recall_metric", recall_metric)
graph_builder.add_node("recall_value", recall_value)
graph_builder.add_node("merge_recall_info", merge_recall_info)
graph_builder.add_node("filter_metric", filter_metric)
graph_builder.add_node("filter_table", filter_table)
graph_builder.add_node("add_context", add_context)
graph_builder.add_node("generate_sql", generate_sql)
graph_builder.add_node("validate_sql", validate_sql)
graph_builder.add_node("corrected_sql",corrected_sql)
graph_builder.add_node("execute_sql", execute_sql)

graph_builder.add_edge(START, "extract_keyword")
graph_builder.add_edge("extract_keyword","recall_column")
graph_builder.add_edge("extract_keyword","recall_metric")
graph_builder.add_edge("extract_keyword", "recall_value")
graph_builder.add_edge("recall_column", "merge_recall_info")
graph_builder.add_edge("recall_metric", "merge_recall_info")
graph_builder.add_edge("recall_value", "merge_recall_info")
graph_builder.add_edge("merge_recall_info", "filter_metric")
graph_builder.add_edge("merge_recall_info", "filter_table")
graph_builder.add_edge("filter_metric", "add_context")
graph_builder.add_edge("filter_table", "add_context")
graph_builder.add_edge("add_context", "generate_sql")
graph_builder.add_edge("generate_sql", "validate_sql")
graph_builder.add_conditional_edges(source="validate_sql",
                                    path= lambda state:"execute_sql" if state['error'] is None else "corrected_sql",
                                    path_map={"execute_sql": "execute_sql", "corrected_sql": "corrected_sql"})
graph_builder.add_edge("corrected_sql", "execute_sql")
graph_builder.add_edge("execute_sql", END)


graph = graph_builder.compile()

print(graph.get_graph().draw_ascii())





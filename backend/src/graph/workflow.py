'''
This module defines the DAG that orchestrate the video compliance audit process pipeline
It connects nodes using the StateGraph from LngGraph

Start -> [Index_VIDEO_ NODE] -> [AUDIT_CONTENT_NODE] -> END
'''

from langgraph.graph import StateGraph, END
from backend.src.graph.state import VideoAuditState

from backend.src.graph.nodes import (
    index_video_node,
    audit_content_node
)

def create_graph():
    """
    Contructs and compiles LangGraph workflow

    returns: Compiled runnable graph object ready for execution
    """

    #1: Initializing the Graph with State Schema(So that the graph adheres to 'VideoAuditState' data structure)
    workflow = StateGraph(VideoAuditState)

    #2: Adding Nodes
    # arg1 -> Unique Name of node, 
    # arg2 -> funtion ot execute 
    workflow.add_node("indexer", index_video_node)
    workflow.add_node("auditor", audit_content_node)

    #3: Defining edges
    #Defining the entry point
    workflow.set_entry_point("indexer")
    workflow.add_edge("indexer", "auditor")
    workflow.add_edge("auditor", END)

    #4: Compling the graph -> Validates the connection and executables runnable
    app = workflow.compile()
    return app

#Expose therunnable app for import by api or cli
app = create_graph()

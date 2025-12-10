import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from .tools import TOOL_REGISTRY

State = Dict[str, Any]

@dataclass
class Node:
    name: str
    tool_name: str

@dataclass
class Graph:
    graph_id: str
    nodes: Dict[str, Node]
    edges: Dict[str, Union[str, Dict[str, str]]]
    start_node: str

@dataclass
class Run:
    run_id: str
    graph_id: str
    current_node: Optional[str]
    state: State
    log: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "running"  # running / completed / failed

# In-memory storage
GRAPHS: Dict[str, Graph] = {}
RUNS: Dict[str, Run] = {}
def create_graph(
    nodes_def: Dict[str, str],
    edges_def: Dict[str, Union[str, Dict[str, str]]],
    start_node: str
) -> Graph:
    graph_id = str(uuid.uuid4())
    nodes = {
        node_name: Node(name=node_name, tool_name=tool_name)
        for node_name, tool_name in nodes_def.items()
    }
    graph = Graph(
        graph_id=graph_id,
        nodes=nodes,
        edges=edges_def,
        start_node=start_node
    )
    GRAPHS[graph_id] = graph
    return graph


def run_graph(graph_id: str, initial_state: State) -> Run:
    graph = GRAPHS[graph_id]
    run_id = str(uuid.uuid4())
    run = Run(
        run_id=run_id,
        graph_id=graph_id,
        current_node=graph.start_node,
        state=initial_state
    )
    RUNS[run_id] = run

    while run.current_node is not None:
        node_name = run.current_node
        node = graph.nodes[node_name]

        tool = TOOL_REGISTRY.get(node.tool_name)
        if tool is None:
            run.status = "failed"
            run.log.append({"node": node_name, "error": f"Tool {node.tool_name} not found"})
            break

        try:
            run.state = tool(run.state)
        except Exception as e:
            run.status = "failed"
            run.log.append({"node": node_name, "error": str(e)})
            break

        run.log.append({"node": node_name, "state": dict(run.state)})

        edge = graph.edges.get(node_name)

        if edge is None:
            run.current_node = None
            run.status = "completed"
            break

        if isinstance(edge, dict):
            branch_key = run.state.get("branch_key")
            run.current_node = edge.get(branch_key)
        else:
            run.current_node = edge

        if run.current_node is None:
            run.status = "completed"

    return run

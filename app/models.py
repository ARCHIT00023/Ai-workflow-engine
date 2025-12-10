from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel

class GraphCreateRequest(BaseModel):
    nodes: Dict[str, str]  # node_name -> tool_name
    edges: Dict[str, Union[str, Dict[str, str]]]  # node_name -> next node OR branch map
    start_node: str

class GraphCreateResponse(BaseModel):
    graph_id: str

class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

class StepLog(BaseModel):
    node: str
    state: Dict[str, Any]

class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    log: List[StepLog]

class RunStateResponse(BaseModel):
    run_id: str
    graph_id: str
    state: Dict[str, Any]
    status: str
    current_node: Optional[str]
    log: List[StepLog]

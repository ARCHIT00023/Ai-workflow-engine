from fastapi import FastAPI, HTTPException

from .models import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    RunStateResponse,
    StepLog,
)
from .engine import create_graph, run_graph, GRAPHS, RUNS
from .workflows import get_code_review_workflow_definition

app = FastAPI(title="Minimal Agent Workflow Engine")

@app.post("/graph/create", response_model=GraphCreateResponse)
def create_graph_endpoint(payload: GraphCreateRequest):
    graph = create_graph(
        nodes_def=payload.nodes,
        edges_def=payload.edges,
        start_node=payload.start_node
    )
    return GraphCreateResponse(graph_id=graph.graph_id)


@app.post("/graph/create/code-review", response_model=GraphCreateResponse)
def create_code_review_graph():
    nodes, edges, start_node = get_code_review_workflow_definition()
    graph = create_graph(nodes_def=nodes, edges_def=edges, start_node=start_node)
    return GraphCreateResponse(graph_id=graph.graph_id)


@app.post("/graph/run", response_model=GraphRunResponse)
def run_graph_endpoint(payload: GraphRunRequest):
    if payload.graph_id not in GRAPHS:
        raise HTTPException(status_code=404, detail="Graph not found")

    run = run_graph(graph_id=payload.graph_id, initial_state=payload.initial_state)

    logs = [
        StepLog(node=entry["node"], state=entry["state"])
        for entry in run.log
        if "state" in entry
    ]

    return GraphRunResponse(
        run_id=run.run_id,
        final_state=run.state,
        log=logs,
    )


@app.get("/graph/state/{run_id}", response_model=RunStateResponse)
def get_run_state(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    logs = [
        StepLog(node=entry.get("node", ""), state=entry.get("state", {}))
        for entry in run.log
        if "state" in entry
    ]

    return RunStateResponse(
        run_id=run.run_id,
        graph_id=run.graph_id,
        state=run.state,
        status=run.status,
        current_node=run.current_node,
        log=logs
    )

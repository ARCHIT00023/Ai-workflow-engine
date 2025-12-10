from typing import Dict, Union

def get_code_review_workflow_definition():
    nodes = {
        "extract": "extract_functions",
        "complexity": "check_complexity",
        "issues": "detect_issues",
        "suggest": "suggest_improvements",
        "loop_check": "check_quality_loop_condition",
    }

    edges: Dict[str, Union[str, Dict[str, str]]] = {
        "extract": "complexity",
        "complexity": "issues",
        "issues": "suggest",
        "suggest": "loop_check",
        "loop_check": {
            "continue": "extract",
            "stop": None
        }
    }

    start_node = "extract"
    return nodes, edges, start_node

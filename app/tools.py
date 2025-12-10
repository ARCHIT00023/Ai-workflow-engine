from typing import Dict, Any, Callable

ToolState = Dict[str, Any]
TOOL_REGISTRY: Dict[str, Callable[[ToolState], ToolState]] = {}

def register_tool(name: str):
    def decorator(func):
        TOOL_REGISTRY[name] = func
        return func
    return decorator

@register_tool("extract_functions")
def extract_functions(state: ToolState) -> ToolState:
    code = state.get("code", "")
    functions = [
        line.strip()
        for line in code.splitlines()
        if line.strip().startswith("def ")
    ]
    state["functions"] = functions
    state["function_count"] = len(functions)
    return state

@register_tool("check_complexity")
def check_complexity(state: ToolState) -> ToolState:
    code = state.get("code", "")
    lines = [l for l in code.splitlines() if l.strip()]
    complexity_score = min(len(lines) / 10, 10)  # simple heuristic
    state["complexity_score"] = complexity_score
    state["complexity_level"] = "high" if complexity_score > 5 else "low"
    return state

@register_tool("detect_issues")
def detect_issues(state: ToolState) -> ToolState:
    code = state.get("code", "")
    issues = 0
    if "TODO" in code:
        issues += code.count("TODO")
    state["issues"] = issues
    return state

@register_tool("suggest_improvements")
def suggest_improvements(state: ToolState) -> ToolState:
    suggestions = []

    if state.get("complexity_score", 0) > 5:
        suggestions.append("Reduce function size or refactor into smaller functions.")
    if state.get("issues", 0) > 0:
        suggestions.append("Resolve TODO comments and pending issues.")
    if not suggestions:
        suggestions.append("Code looks good overall.")

    # quality_score: toy formula
    complexity_penalty = state.get("complexity_score", 0)
    issue_penalty = state.get("issues", 0)
    quality_score = max(0, min(10, 10 - (complexity_penalty + issue_penalty)))

    state["suggestions"] = suggestions
    state["quality_score"] = quality_score
    return state

@register_tool("check_quality_loop_condition")
def check_quality_loop_condition(state: ToolState) -> ToolState:
    threshold = state.get("quality_threshold", 8)
    quality = state.get("quality_score", 0)
    if quality < threshold:
        state["branch_key"] = "continue"
    else:
        state["branch_key"] = "stop"
    return state

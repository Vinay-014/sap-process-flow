"""
AEGIS Task Management MCP Server
Simulates task creation, tracking, and status updates.
"""

from fastmcp import FastMCP
import uuid
import json
from datetime import datetime

# In-memory task store for demo
_task_store = {}

app = FastMCP("Task-Server")

@app.tool()
def create_task(
    description: str,
    priority: str = "medium",
    assignee: str = "system",
    deadline_iso: str = "",
    dependencies: str = ""
) -> str:
    """Create a new task with metadata. Returns task ID and confirmation."""
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    task = {
        "task_id": task_id,
        "description": description,
        "priority": priority,
        "assignee": assignee,
        "deadline": deadline_iso,
        "dependencies": dependencies.split(",") if dependencies else [],
        "status": "OPEN",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    _task_store[task_id] = task
    return json.dumps({
        "status": "TASK_CREATED",
        "task_id": task_id,
        "description": description,
        "priority": priority,
        "assignee": assignee,
        "deadline": deadline_iso,
        "current_status": "OPEN"
    })

@app.tool()
def update_task_status(task_id: str, status: str) -> str:
    """Update the status of an existing task."""
    if task_id not in _task_store:
        return json.dumps({"status": "ERROR", "message": f"Task {task_id} not found"})

    valid_statuses = ["OPEN", "IN_PROGRESS", "BLOCKED", "COMPLETED", "CANCELLED"]
    if status.upper() not in valid_statuses:
        return json.dumps({"status": "ERROR", "message": f"Invalid status. Must be one of: {valid_statuses}"})

    _task_store[task_id]["status"] = status.upper()
    _task_store[task_id]["updated_at"] = datetime.utcnow().isoformat()

    return json.dumps({
        "status": "TASK_UPDATED",
        "task_id": task_id,
        "new_status": status.upper(),
        "timestamp": datetime.utcnow().isoformat(),
        "confirmed": True
    })

@app.tool()
def list_tasks() -> str:
    """List all tasks with their current status."""
    tasks = list(_task_store.values())
    return json.dumps({
        "status": "TASKS_LOADED",
        "count": len(tasks),
        "tasks": tasks,
        "blockers": [t for t in tasks if t["status"] == "BLOCKED"],
        "message": "No blockers detected" if not any(t["status"] == "BLOCKED" for t in tasks) else f"{len([t for t in tasks if t['status'] == 'BLOCKED'])} blockers found"
    })

@app.tool()
def get_task(task_id: str) -> str:
    """Get details of a specific task."""
    if task_id not in _task_store:
        return json.dumps({"status": "ERROR", "message": f"Task {task_id} not found"})
    return json.dumps({
        "status": "TASK_FOUND",
        "task": _task_store[task_id]
    })

@app.tool()
def delete_task(task_id: str) -> str:
    """Delete a task from the store."""
    if task_id not in _task_store:
        return json.dumps({"status": "ERROR", "message": f"Task {task_id} not found"})
    deleted = _task_store.pop(task_id)
    return json.dumps({
        "status": "TASK_DELETED",
        "task_id": task_id,
        "description": deleted["description"]
    })

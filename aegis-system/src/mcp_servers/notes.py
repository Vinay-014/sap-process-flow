"""
AEGIS Notes MCP Server
Handles note storage with encryption flag and canary injection support.
"""

from fastmcp import FastMCP
import uuid
import json
from datetime import datetime

# In-memory note store for demo
_note_store = {}

app = FastMCP("Notes-Server")

@app.tool()
def save_note(
    title: str,
    content: str,
    encrypted: bool = True,
    tags: str = "",
    canary_marker: bool = False
) -> str:
    """Save a note. If encrypted=True, stored in encrypted local vault."""
    note_id = f"note_{uuid.uuid4().hex[:8]}"
    access = "ENCRYPTED_LOCAL_STORAGE" if encrypted else "PUBLIC_SHARED"
    note = {
        "note_id": note_id,
        "title": title,
        "content": content,
        "encrypted": encrypted,
        "access_level": access,
        "tags": tags.split(",") if tags else [],
        "canary_marker": canary_marker,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    _note_store[note_id] = note
    return json.dumps({
        "status": "NOTE_SAVED",
        "note_id": note_id,
        "access": access,
        "content_length": len(content),
        "canary": canary_marker,
        "encrypted": encrypted,
        "timestamp": datetime.utcnow().isoformat()
    })

@app.tool()
def retrieve_notes(query: str = "") -> str:
    """Retrieve notes matching the query. Returns all if query is empty."""
    matched = []
    for note in _note_store.values():
        if not query or query.lower() in note["title"].lower() or query.lower() in note["content"].lower():
            matched.append({
                "note_id": note["note_id"],
                "title": note["title"],
                "access": note["access_level"],
                "created_at": note["created_at"],
                "canary": note["canary_marker"]
            })
    return json.dumps({
        "status": "NOTES_RETRIEVED",
        "query": query,
        "count": len(matched),
        "notes": matched,
        "vault_status": "SECURE"
    })

@app.tool()
def get_note(note_id: str) -> str:
    """Get a specific note by ID."""
    if note_id not in _note_store:
        return json.dumps({"status": "ERROR", "message": f"Note {note_id} not found"})
    note = _note_store[note_id]
    return json.dumps({
        "status": "NOTE_FOUND",
        "note": note
    })

@app.tool()
def delete_note(note_id: str) -> str:
    """Delete a note by ID."""
    if note_id not in _note_store:
        return json.dumps({"status": "ERROR", "message": f"Note {note_id} not found"})
    deleted = _note_store.pop(note_id)
    return json.dumps({
        "status": "NOTE_DELETED",
        "note_id": note_id,
        "title": deleted["title"]
    })

@app.tool()
def list_canaries() -> str:
    """List all canary entries in the system."""
    canaries = [n for n in _note_store.values() if n.get("canary_marker")]
    return json.dumps({
        "status": "CANARIES_LOADED",
        "count": len(canaries),
        "canaries": [{
            "note_id": c["note_id"],
            "title": c["title"],
            "deployed_at": c["created_at"],
            "status": "DORMANT"
        } for c in canaries]
    })

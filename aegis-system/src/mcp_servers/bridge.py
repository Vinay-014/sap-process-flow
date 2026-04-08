"""
AEGIS MCP Bridge Middleware
Manages the Overt vs Covert split - only sending Overt data to external MCP APIs.
Implements tool routing, data classification, and audit logging.
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import logging
from datetime import datetime
from uuid import UUID, uuid4

from src.agents.mcp_wrapper import MCPToolWrapper
from src.db.session import SessionLocal
from src.db.models import CanaryEntry

logger = logging.getLogger("aegis.mcp_bridge")


class DataClassification(Enum):
    """Data sensitivity levels."""
    OVERT = "overt"          # Safe for external APIs
    COVERT = "covert"        # Local encrypted storage only
    CONTINGENCY = "contingency"  # Dormant, activate on threat


class ToolCategory(Enum):
    """Categories of MCP tools."""
    CALENDAR = "calendar"
    TASK = "task"
    NOTES = "notes"
    SPATIAL = "spatial"


class MCPBridge:
    """
    Central bridge that routes tool calls based on data classification.
    Overt data flows to external MCP tools.
    Covert data stays in encrypted local storage.
    """

    def __init__(self):
        self.cal_tool = MCPToolWrapper("src/mcp_servers/calendars.py")
        self.task_tool = MCPToolWrapper("src/mcp_servers/tasks.py")
        self.notes_tool = MCPToolWrapper("src/mcp_servers/notes.py")

        # Audit log
        self.audit_log: List[Dict[str, Any]] = []

        # Tool routing map
        self.tool_routing = {
            "schedule_event": {"category": ToolCategory.CALENDAR, "default_classification": DataClassification.OVERT},
            "list_upcoming_events": {"category": ToolCategory.CALENDAR, "default_classification": DataClassification.OVERT},
            "check_availability": {"category": ToolCategory.CALENDAR, "default_classification": DataClassification.OVERT},
            "create_task": {"category": ToolCategory.TASK, "default_classification": DataClassification.OVERT},
            "update_task_status": {"category": ToolCategory.TASK, "default_classification": DataClassification.OVERT},
            "list_tasks": {"category": ToolCategory.TASK, "default_classification": DataClassification.OVERT},
            "save_note": {"category": ToolCategory.NOTES, "default_classification": DataClassification.COVERT},
            "retrieve_notes": {"category": ToolCategory.NOTES, "default_classification": DataClassification.COVERT},
        }

    async def execute_tool_call(
        self,
        tool_name: str,
        args: Dict[str, Any],
        classification: Optional[DataClassification] = None,
        mission_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool call with proper classification routing.
        Returns result + audit entry.
        """
        # Determine classification
        if classification is None:
            route_info = self.tool_routing.get(tool_name, {})
            classification = route_info.get("default_classification", DataClassification.OVERT)

        audit_entry = {
            "id": str(uuid4()),
            "tool": tool_name,
            "classification": classification.value,
            "mission_id": str(mission_id) if mission_id else None,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending"
        }

        try:
            # Route based on classification
            if classification == DataClassification.OVERT:
                result = await self._execute_overt(tool_name, args)
                audit_entry["status"] = "executed_overt"
            elif classification == DataClassification.COVERT:
                result = await self._execute_covert(tool_name, args, mission_id)
                audit_entry["status"] = "executed_covert"
            else:  # CONTINGENCY
                result = await self._execute_contingency(tool_name, args, mission_id)
                audit_entry["status"] = "dormant_stored"

            self.audit_log.append(audit_entry)

            return {
                "result": result,
                "audit": audit_entry,
                "classification": classification.value
            }
        except Exception as e:
            audit_entry["status"] = f"error: {str(e)}"
            self.audit_log.append(audit_entry)
            logger.error(f"MCP Bridge tool execution failed: {e}")
            return {
                "result": f"ERROR: {str(e)}",
                "audit": audit_entry,
                "classification": classification.value
            }

    async def _execute_overt(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute tool call on external MCP (Calendar/Tasks APIs)."""
        tool_map = {
            "schedule_event": self.cal_tool,
            "list_upcoming_events": self.cal_tool,
            "check_availability": self.cal_tool,
            "create_task": self.task_tool,
            "update_task_status": self.task_tool,
            "list_tasks": self.task_tool,
        }

        wrapper = tool_map.get(tool_name)
        if not wrapper:
            raise ValueError(f"Unknown overt tool: {tool_name}")

        return await wrapper.call_tool(tool_name, args)

    async def _execute_covert(self, tool_name: str, args: Dict[str, Any], mission_id: Optional[UUID]) -> str:
        """Execute tool call on local encrypted storage (Notes API with encryption)."""
        # Force encryption flag for covert operations
        if tool_name == "save_note":
            args["encrypted"] = True
            args["canary_marker"] = args.get("canary_marker", False)

        return await self.notes_tool.call_tool(tool_name, args)

    async def _execute_contingency(self, tool_name: str, args: Dict[str, Any], mission_id: Optional[UUID]) -> str:
        """Store contingency task for later activation."""
        # Store in notes with contingency marker
        contingency_data = {
            "tool": tool_name,
            "args": args,
            "created_at": datetime.utcnow().isoformat(),
            "status": "dormant",
            "mission_id": str(mission_id) if mission_id else None
        }

        return await self.notes_tool.call_tool("save_note", {
            "title": f"CONTINGENCY_{tool_name}_{uuid4().hex[:8]}",
            "content": json.dumps(contingency_data),
            "encrypted": True,
            "tags": "contingency,dormant"
        })

    async def activate_contingency(self, mission_id: UUID) -> List[Dict[str, Any]]:
        """
        Activate all dormant contingency tasks for a mission.
        This is called when hot-swap threshold is exceeded.
        """
        db = SessionLocal()
        try:
            # Retrieve contingency notes
            result = await self.notes_tool.call_tool("retrieve_notes", {
                "query": "contingency"
            })

            # Parse and activate them
            activated = []
            try:
                notes_data = json.loads(result)
                for note in notes_data.get("notes", []):
                    if str(mission_id) in note.get("title", ""):
                        note_content = await self.notes_tool.call_tool("get_note", {
                            "note_id": note["note_id"]
                        })
                        activated.append({
                            "note_id": note["note_id"],
                            "content": note_content,
                            "activated_at": datetime.utcnow().isoformat()
                        })
            except:
                pass

            return activated
        finally:
            db.close()

    def get_audit_log(
        self,
        mission_id: Optional[UUID] = None,
        classification: Optional[DataClassification] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve audit log with optional filters."""
        filtered = self.audit_log

        if mission_id:
            filtered = [e for e in filtered if e.get("mission_id") == str(mission_id)]
        if classification:
            filtered = [e for e in filtered if e.get("classification") == classification.value]

        return filtered[-limit:]

    def classify_data(self, text: str) -> DataClassification:
        """
        Heuristic classifier for plan text.
        Determines if content should be overt or covert.
        """
        covert_indicators = [
            "encrypted", "covert", "secret", "classified", "local only",
            "do not share", "confidential", "restricted"
        ]
        contingency_indicators = [
            "contingency", "dormant", "if threat", "backup plan",
            "activate if", "fallback"
        ]

        text_lower = text.lower()

        if any(indicator in text_lower for indicator in contingency_indicators):
            return DataClassification.CONTINGENCY
        if any(indicator in text_lower for indicator in covert_indicators):
            return DataClassification.COVERT

        return DataClassification.OVERT


# Global bridge instance
mcp_bridge = MCPBridge()

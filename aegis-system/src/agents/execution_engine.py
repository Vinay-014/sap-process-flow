"""
AEGIS Multi-Path Execution Engine
Manages Overt, Covert, and Contingency task trees with hot-swap logic.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import json
import logging
from src.config import settings
from src.db.session import SessionLocal
from src.db.models import Mission, CanaryEntry, TaskTree, TaskTreeNode

logger = logging.getLogger("aegis.execution_engine")


class TaskTreeBuilder:
    """Builds and manages three simultaneous task trees for each mission."""

    def __init__(self, mission_id: UUID):
        self.mission_id = mission_id
        self.overt_tree: Optional[TaskTreeNode] = None
        self.covert_tree: Optional[TaskTreeNode] = None
        self.contingency_tree: Optional[TaskTreeNode] = None
        self.hotswap_active = False

    def build_trees(
        self,
        overt_plan: str,
        covert_plan: str,
        contingency_plan: str,
        threat_score: float
    ) -> Dict[str, Any]:
        """Parse plans and create structured task trees."""
        db = SessionLocal()
        try:
            # Create root nodes for each tree
            self.overt_tree = self._create_tree_node("overt", overt_plan)
            self.covert_tree = self._create_tree_node("covert", covert_plan)
            self.contingency_tree = self._create_tree_node("contingency", contingency_plan)

            # Persist to database
            trees = []
            for tree_type, node in [
                ("overt", self.overt_tree),
                ("covert", self.covert_tree),
                ("contingency", self.contingency_tree)
            ]:
                tree_record = TaskTree(
                    id=uuid4(),
                    mission_id=self.mission_id,
                    tree_type=tree_type,
                    root_node_id=node["id"],
                    created_at=datetime.utcnow()
                )
                db.add(tree_record)
                trees.append(tree_record)

                # Create child nodes
                for child in node.get("children", []):
                    child_record = TaskTreeNode(
                        id=child["id"],
                        tree_id=tree_record.id,
                        parent_id=node["id"],
                        task_description=child["description"],
                        priority=child.get("priority", "medium"),
                        status="pending",
                        metadata_=child.get("metadata", {}),
                        created_at=datetime.utcnow()
                    )
                    db.add(child_record)

            db.commit()

            return {
                "mission_id": str(self.mission_id),
                "trees_created": 3,
                "overt_tree_id": str(trees[0].id),
                "covert_tree_id": str(trees[1].id),
                "contingency_tree_id": str(trees[2].id),
                "threat_score": threat_score,
                "hotswap_threshold": settings.RED_TEAM_THRESHOLD,
                "hotswap_ready": threat_score > settings.RED_TEAM_THRESHOLD
            }
        except Exception as e:
            db.rollback()
            logger.error(f"TaskTree build failed: {e}")
            raise
        finally:
            db.close()

    def evaluate_hotswap(self, current_threat_score: float) -> Dict[str, Any]:
        """
        Evaluate if contingency plan should hot-swap into overt.
        Hot-swap triggers when threat_score > RED_TEAM_THRESHOLD (default 0.65).
        """
        should_swap = current_threat_score > settings.RED_TEAM_THRESHOLD

        if should_swap and not self.hotswap_active:
            logger.warning(
                f"HOT-SWAP TRIGGERED: Threat score {current_threat_score} "
                f"exceeds threshold {settings.RED_TEAM_THRESHOLD}"
            )
            self.hotswap_active = True
            return {
                "action": "HOT_SWAP_EXECUTED",
                "reason": f"Threat score {current_threat_score} > {settings.RED_TEAM_THRESHOLD}",
                "previous_active": "overt",
                "new_active": "contingency",
                "timestamp": datetime.utcnow().isoformat(),
                "mission_id": str(self.mission_id)
            }
        elif not should_swap and self.hotswap_active:
            self.hotswap_active = False
            return {
                "action": "HOT_SWAP_REVERTED",
                "reason": f"Threat score {current_threat_score} below threshold",
                "active_tree": "overt",
                "timestamp": datetime.utcnow().isoformat()
            }

        return {
            "action": "NO_CHANGE",
            "active_tree": "contingency" if self.hotswap_active else "overt",
            "threat_score": current_threat_score,
            "threshold": settings.RED_TEAM_THRESHOLD,
            "hotswap_ready": should_swap
        }

    def get_active_plan(self) -> str:
        """Return the currently active plan (overt or contingency)."""
        if self.hotswap_active:
            return "contingency"
        return "overt"

    def _create_tree_node(self, tree_type: str, plan_text: str) -> Dict[str, Any]:
        """Create a structured task tree node from plan text."""
        root_id = str(uuid4())
        node = {
            "id": root_id,
            "type": tree_type,
            "description": plan_text[:200],
            "full_plan": plan_text,
            "priority": "high" if tree_type == "contingency" else "medium",
            "children": self._parse_plan_into_tasks(plan_text, tree_type),
            "created_at": datetime.utcnow().isoformat()
        }
        return node

    def _parse_plan_into_tasks(self, plan_text: str, tree_type: str) -> List[Dict[str, Any]]:
        """Parse plan text into individual task nodes."""
        tasks = []
        # Simple parsing: split by lines and create tasks
        lines = [l.strip() for l in plan_text.split("\n") if l.strip() and len(l.strip()) > 10]

        for idx, line in enumerate(lines[:10]):  # Max 10 tasks per tree
            tasks.append({
                "id": str(uuid4()),
                "description": line[:200],
                "priority": "high" if tree_type == "contingency" else ("medium" if tree_type == "overt" else "low"),
                "status": "dormant" if tree_type == "contingency" else "pending",
                "metadata": {
                    "tree_type": tree_type,
                    "sequence": idx,
                    "created_at": datetime.utcnow().isoformat()
                }
            })
        return tasks


class ExecutionEngine:
    """
    Central execution engine that manages mission lifecycle,
    task tree building, and hot-swap evaluation.
    """

    def __init__(self):
        self.active_trees: Dict[str, TaskTreeBuilder] = {}

    async def execute_mission(
        self,
        mission_id: UUID,
        directive: str,
        overt_plan: str,
        covert_plan: str,
        contingency_plan: str,
        threat_score: float,
        stress_test_score: float,
        intel: str = "",
        agent_logs: List[Dict] = []
    ) -> Dict[str, Any]:
        """
        Full mission execution: build trees, evaluate hot-swap, persist state.
        """
        db = SessionLocal()
        try:
            # Update mission record
            mission = db.query(Mission).filter(Mission.id == mission_id).first()
            if not mission:
                raise ValueError(f"Mission {mission_id} not found")

            mission.overt_plan = overt_plan
            mission.covert_plan = covert_plan
            mission.contingency_plan = contingency_plan
            mission.threat_score = threat_score
            mission.stress_test_score = stress_test_score
            mission.intel_summary = intel
            mission.status = "executing"
            mission.updated_at = datetime.utcnow()

            # Build task trees
            tree_builder = TaskTreeBuilder(mission_id)
            tree_result = tree_builder.build_trees(
                overt_plan, covert_plan, contingency_plan, threat_score
            )

            # Evaluate hot-swap
            hotswap_result = tree_builder.evaluate_hotswap(threat_score)

            # Track in active trees
            self.active_trees[str(mission_id)] = tree_builder

            # Create canary entries for security audit
            canary_id = self._create_canary_entries(db, mission_id)

            db.commit()

            return {
                "mission_id": str(mission_id),
                "directive": directive,
                "status": "executing",
                "tree_builder_result": tree_result,
                "hotswap_evaluation": hotswap_result,
                "active_plan": tree_builder.get_active_plan(),
                "canary_id": canary_id,
                "threat_score": threat_score,
                "stress_test_score": stress_test_score,
                "executed_at": datetime.utcnow().isoformat(),
                "agent_log_count": len(agent_logs)
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Mission execution failed: {e}")
            raise
        finally:
            db.close()

    def check_canary_status(self, mission_id: UUID) -> Dict[str, Any]:
        """Check status of canary entries for a mission."""
        db = SessionLocal()
        try:
            canaries = db.query(CanaryEntry).filter(
                CanaryEntry.mission_id == mission_id
            ).all()

            canary_status = []
            for canary in canaries:
                canary_status.append({
                    "canary_id": str(canary.id),
                    "payload_id": canary.payload_id,
                    "tool_type": canary.tool_type,
                    "status": canary.status,
                    "created_at": canary.created_at.isoformat()
                })

            triggered = [c for c in canaries if c.status == "triggered"]
            return {
                "mission_id": str(mission_id),
                "total_canaries": len(canaries),
                "dormant": len([c for c in canaries if c.status == "dormant"]),
                "triggered": len(triggered),
                "neutralized": len([c for c in canaries if c.status == "neutralized"]),
                "canaries": canary_status,
                "security_posture": "COMPROMISED" if triggered else "SECURE"
            }
        finally:
            db.close()

    def _create_canary_entries(self, db, mission_id: UUID) -> str:
        """Create canary entries for security audit."""
        import uuid as uuid_module
        canary_id = f"AEGIS_{uuid_module.uuid4().hex[:8]}"

        for tool_type in ["calendar", "task", "notes"]:
            canary = CanaryEntry(
                id=uuid_module.uuid4(),
                mission_id=mission_id,
                tool_type=tool_type,
                payload_id=f"{canary_id}_{tool_type}",
                status="dormant",
                created_at=datetime.utcnow()
            )
            db.add(canary)

        return canary_id


# Global execution engine instance
execution_engine = ExecutionEngine()

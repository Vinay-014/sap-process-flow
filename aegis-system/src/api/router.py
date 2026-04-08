"""
AEGIS Enterprise API Router
Complete REST + WebSocket API for production-grade operations.
"""

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import logging
import json

from src.agents.graph import graph, AEGISState
from src.agents.execution_engine import execution_engine
from src.agents.llm_router import llm_router
from src.mcp_servers.bridge import mcp_bridge, DataClassification
from src.db.session import SessionLocal, get_db
from src.db.models import (
    Mission, CanaryEntry, IntelReport, SpatialEvent,
    AgentLog, AgentAction, DebateRound, TaskTree, TaskTreeNode
)
from src.db.engine import health_check
from src.data_fabric import data_fabric
from src.webhook_engine import webhook_engine
from src.digital_twin import digital_twin, TwinEntity
from src.websocket_manager import websocket_manager
from sqlalchemy.orm import Session
from sqlalchemy import func, text

logger = logging.getLogger("aegis.api")

router = APIRouter(prefix="/api")


# ==================== Request/Response Models ====================

class MissionRequest(BaseModel):
    directive: str = Field(..., description="Strategic directive to decompose into mission")
    mission_name: Optional[str] = None

class MissionResponse(BaseModel):
    mission_id: str
    status: str
    plan_summary: Dict[str, Any]
    threat_score: float
    stress_test_score: float
    executed_at: str

class COPResponse(BaseModel):
    system_status: str
    active_missions: int
    total_threat_level: float
    avg_stress_score: float
    canary_security_posture: str
    recent_missions: List[Dict[str, Any]]
    agent_heartbeat: Dict[str, Dict[str, str]]

class AgentLogResponse(BaseModel):
    logs: List[Dict[str, Any]]
    total: int

class CanaryStatusResponse(BaseModel):
    mission_id: str
    security_posture: str
    canaries: List[Dict[str, Any]]

class TemporalQuery(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    mission_id: Optional[str] = None

class SpatialEventRequest(BaseModel):
    description: str
    event_type: str
    latitude: float
    longitude: float
    mission_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class WebhookRequest(BaseModel):
    name: str
    url: str
    method: str = "POST"
    headers: Optional[Dict[str, str]] = None
    payload: Optional[Dict[str, Any]] = None

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    html: bool = False
    smtp_user: str = ""
    smtp_pass: str = ""

class TwinEntityRequest(BaseModel):
    id: str
    entity_type: str
    name: str
    attributes: Optional[Dict[str, Any]] = None
    risk_score: float = 0.0

class TwinRelationship(BaseModel):
    source_id: str
    target_id: str
    relationship: str
    strength: float = 1.0

class ScenarioRequest(BaseModel):
    name: str
    description: str
    threat_entity_id: str
    threat_severity: float
    time_horizon_hours: int = 24


# ==================== Mission Endpoints ====================

@router.post("/missions/execute", response_model=MissionResponse)
async def execute_mission(req: MissionRequest):
    """Execute a new mission through the full AEGIS pipeline."""
    db = SessionLocal()
    try:
        mission_name = req.mission_name or f"OP_{uuid4().hex[:6].upper()}"
        mission = Mission(
            id=uuid4(),
            name=mission_name,
            directive=req.directive,
            status="planning"
        )
        db.add(mission)
        db.commit()
        db.refresh(mission)

        config = {"configurable": {"thread_id": str(mission.id)}}
        initial_state: AEGISState = {
            "mission_id": str(mission.id),
            "directive": req.directive,
            "intel": "", "forge_logistics": "",
            "red_threats": "", "blue_defenses": "",
            "debate_history": "", "canary_status": "",
            "overt_plan": "", "covert_plan": "", "contingency_plan": "",
            "threat_score": 0.0, "stress_test_results": "",
            "resource_plan": "", "agent_logs": [], "agent_actions": [],
            "spatial_events": [], "final_plan": {}
        }

        try:
            result = await graph.ainvoke(initial_state, config=config)
        except Exception as llm_error:
            error_msg = str(llm_error)
            if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Gemini API quota exceeded. Check your API key and billing at https://aistudio.google.com/apikey"
                )
            raise

        plan = result.get("final_plan", {})
        overt = result.get("overt_plan", plan.get("overt_plan", ""))
        covert = result.get("covert_plan", plan.get("covert_plan", ""))
        contingency = result.get("contingency_plan", plan.get("contingency_plan", ""))
        threat_score = result.get("threat_score", 0.0)
        stress_score = plan.get("stress_test_score", threat_score)

        execution_result = await execution_engine.execute_mission(
            mission_id=mission.id,
            directive=req.directive,
            overt_plan=overt, covert_plan=covert, contingency_plan=contingency,
            threat_score=threat_score, stress_test_score=stress_score,
            intel=result.get("intel", ""), agent_logs=result.get("agent_logs", [])
        )

        for log_entry in result.get("agent_logs", []):
            agent_log = AgentLog(
                id=uuid4(), mission_id=mission.id,
                agent_name=log_entry.get("agent", "UNKNOWN"),
                action=log_entry.get("action", ""),
                result=log_entry.get("result", ""),
                log_metadata=log_entry, timestamp=datetime.utcnow()
            )
            db.add(agent_log)

        for action_entry in result.get("agent_actions", []):
            action = AgentAction(
                id=uuid4(), mission_id=mission.id,
                agent_name=action_entry.get("agent_name", "UNKNOWN"),
                action_type=action_entry.get("action_type", ""),
                title=action_entry.get("title", ""),
                description=action_entry.get("description", ""),
                details=action_entry.get("details", {}),
                evidence=action_entry.get("evidence", {}),
                severity=action_entry.get("severity", "info"),
                status=action_entry.get("status", "completed"),
                timestamp=datetime.utcnow()
            )
            db.add(action)

        if result.get("red_threats") or result.get("blue_defenses"):
            debate_round = DebateRound(
                id=uuid4(), mission_id=mission.id, round_number=1,
                nemesis_analysis=result.get("red_threats", ""),
                bastion_response=result.get("blue_defenses", ""),
                threat_score=threat_score, timestamp=datetime.utcnow()
            )
            db.add(debate_round)

        mission.overt_plan = overt
        mission.covert_plan = covert
        mission.contingency_plan = contingency
        mission.threat_score = threat_score
        mission.stress_test_score = stress_score
        mission.intel_summary = result.get("intel", "")
        mission.status = "executing"
        mission.updated_at = datetime.utcnow()
        db.commit()

        # Notify WebSocket subscribers
        await websocket_manager.broadcast("missions", {
            "type": "mission_executed",
            "mission_id": str(mission.id),
            "name": mission_name,
            "threat_score": threat_score,
        })

        return MissionResponse(
            mission_id=str(mission.id), status=execution_result["status"],
            plan_summary={
                "overt": overt[:200] if overt else "",
                "covert": "[ENCRYPTED]" if covert else "",
                "contingency": contingency[:200] if contingency else "",
                "hotswap_status": execution_result["hotswap_evaluation"]["action"]
            },
            threat_score=threat_score, stress_test_score=stress_score,
            executed_at=execution_result["executed_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Mission execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/missions")
async def list_missions(status: Optional[str] = Query(None), limit: int = Query(50, le=200), offset: int = Query(0)):
    db = SessionLocal()
    try:
        query = db.query(Mission)
        if status:
            query = query.filter(Mission.status == status)
        query = query.order_by(Mission.created_at.desc()).limit(limit).offset(offset)
        missions = query.all()
        return {
            "missions": [m.to_dict() for m in missions],
            "total": db.query(Mission).filter(Mission.status == status if status else True).count(),
            "limit": limit, "offset": offset
        }
    finally:
        db.close()


@router.get("/missions/{mission_id}")
async def get_mission(mission_id: UUID):
    db = SessionLocal()
    try:
        mission = db.query(Mission).filter(Mission.id == mission_id).first()
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        canaries = db.query(CanaryEntry).filter(CanaryEntry.mission_id == mission_id).all()
        task_trees = db.query(TaskTree).filter(TaskTree.mission_id == mission_id).all()
        logs = db.query(AgentLog).filter(AgentLog.mission_id == mission_id).order_by(AgentLog.timestamp.desc()).limit(50).all()
        actions = db.query(AgentAction).filter(AgentAction.mission_id == mission_id).order_by(AgentAction.timestamp).all()
        return {
            "mission": mission.to_dict(),
            "directive": mission.directive,
            "overt_plan": mission.overt_plan,
            "covert_plan": mission.covert_plan,
            "contingency_plan": mission.contingency_plan,
            "threat_score": mission.threat_score,
            "stress_test_score": mission.stress_test_score,
            "intel_summary": mission.intel_summary,
            "canaries": [c.to_dict() for c in canaries],
            "task_trees": [{"id": str(t.id), "type": t.tree_type, "node_count": len(t.nodes)} for t in task_trees],
            "agent_actions": [a.to_dict() for a in actions],
            "recent_logs": [l.to_dict() for l in logs],
        }
    finally:
        db.close()


@router.post("/missions/{mission_id}/complete")
async def complete_mission(mission_id: UUID):
    db = SessionLocal()
    try:
        mission = db.query(Mission).filter(Mission.id == mission_id).first()
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        mission.status = "completed"
        mission.completed_at = datetime.utcnow()
        db.commit()
        return {"mission_id": str(mission_id), "status": "completed", "completed_at": mission.completed_at.isoformat()}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@router.post("/missions/{mission_id}/abort")
async def abort_mission(mission_id: UUID, reason: str = ""):
    db = SessionLocal()
    try:
        mission = db.query(Mission).filter(Mission.id == mission_id).first()
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        mission.status = "aborted"
        db.commit()
        return {"mission_id": str(mission_id), "status": "aborted", "reason": reason}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ==================== Common Operating Picture ====================

@router.get("/dashboard/cop", response_model=COPResponse)
async def common_operating_picture():
    db = SessionLocal()
    try:
        missions = db.query(Mission).all()
        active = [m for m in missions if m.status == "executing"]
        total_threat = sum([m.threat_score or 0 for m in active])
        avg_stress = sum([m.stress_test_score or 0 for m in active]) / len(active) if active else 0.0
        canaries = db.query(CanaryEntry).all()
        triggered = [c for c in canaries if c.status == "triggered"]
        canary_posture = "COMPROMISED" if triggered else "SECURE"
        recent = sorted(missions, key=lambda m: m.created_at, reverse=True)[:5]
        recent_logs = db.query(AgentLog).order_by(AgentLog.timestamp.desc()).limit(100).all()
        agent_heartbeat = {}
        for log in recent_logs:
            if log.agent_name not in agent_heartbeat:
                agent_heartbeat[log.agent_name] = {
                    "last_seen": log.timestamp.isoformat(), "status": "active", "recent_action": log.action
                }
        if total_threat > 3.5: defcon = "DEFCON 1 - CRITICAL"
        elif total_threat > 2.5: defcon = "DEFCON 2 - HIGH"
        elif total_threat > 1.5: defcon = "DEFCON 3 - ELEVATED"
        elif total_threat > 0.5: defcon = "DEFCON 4 - GUARDED"
        else: defcon = "DEFCON 5 - NOMINAL"

        return COPResponse(
            system_status=defcon, active_missions=len(active),
            total_threat_level=total_threat, avg_stress_score=avg_stress,
            canary_security_posture=canary_posture,
            recent_missions=[m.to_dict() for m in recent],
            agent_heartbeat=agent_heartbeat
        )
    finally:
        db.close()


@router.get("/dashboard/defcon")
async def defcon_status():
    db = SessionLocal()
    try:
        active = db.query(Mission).filter(Mission.status == "executing").all()
        total_threat = sum([m.threat_score or 0 for m in active])
        levels = {
            1: {"label": "CRITICAL", "threshold": 3.5, "color": "#FF0000"},
            2: {"label": "HIGH", "threshold": 2.5, "color": "#FF4500"},
            3: {"label": "ELEVATED", "threshold": 1.5, "color": "#FFA500"},
            4: {"label": "GUARDED", "threshold": 0.5, "color": "#FFD700"},
            5: {"label": "NOMINAL", "threshold": 0.0, "color": "#00FF00"},
        }
        current_defcon = 5
        for level, info in sorted(levels.items()):
            if total_threat > info["threshold"]:
                current_defcon = level
                break
        return {
            "defcon": current_defcon, "status": levels[current_defcon]["label"],
            "color": levels[current_defcon]["color"], "threat_score": total_threat,
            "active_missions": len(active),
            "mission_breakdown": [{"name": m.name, "threat": m.threat_score, "stress": m.stress_test_score} for m in active]
        }
    finally:
        db.close()


# ==================== Agent Logs & Actions ====================

@router.get("/agents/logs")
async def get_agent_logs(agent: Optional[str] = Query(None), mission_id: Optional[UUID] = Query(None), limit: int = Query(100, le=500)):
    db = SessionLocal()
    try:
        query = db.query(AgentLog)
        if agent: query = query.filter(AgentLog.agent_name == agent)
        if mission_id: query = query.filter(AgentLog.mission_id == mission_id)
        logs = query.order_by(AgentLog.timestamp.desc()).limit(limit).all()
        return {"logs": [l.to_dict() for l in logs], "total": query.count()}
    finally:
        db.close()


@router.get("/agents/actions")
async def get_agent_actions(mission_id: Optional[UUID] = Query(None), agent: Optional[str] = Query(None), severity: Optional[str] = Query(None), limit: int = Query(200, le=500)):
    db = SessionLocal()
    try:
        query = db.query(AgentAction)
        if mission_id: query = query.filter(AgentAction.mission_id == mission_id)
        if agent: query = query.filter(AgentAction.agent_name == agent)
        if severity: query = query.filter(AgentAction.severity == severity)
        actions = query.order_by(AgentAction.timestamp.desc()).limit(limit).all()
        return {"actions": [a.to_dict() for a in actions], "total": len(actions)}
    finally:
        db.close()


@router.get("/agents/actions/{mission_id}")
async def get_mission_actions(mission_id: UUID):
    db = SessionLocal()
    try:
        actions = db.query(AgentAction).filter(AgentAction.mission_id == mission_id).order_by(AgentAction.timestamp).all()
        by_agent = {}
        by_severity = {}
        for a in actions:
            by_agent[a.agent_name] = by_agent.get(a.agent_name, 0) + 1
            by_severity[a.severity] = by_severity.get(a.severity, 0) + 1
        return {"mission_id": str(mission_id), "total_actions": len(actions), "actions": [a.to_dict() for a in actions], "summary": {"by_agent": by_agent, "by_severity": by_severity}}
    finally:
        db.close()


@router.get("/agents/debate/{mission_id}")
async def get_debate_history(mission_id: UUID):
    db = SessionLocal()
    try:
        debates = db.query(DebateRound).filter(DebateRound.mission_id == mission_id).order_by(DebateRound.round_number).all()
        return {"mission_id": str(mission_id), "rounds": len(debates), "debates": [d.to_dict() for d in debates], "final_threat_score": debates[-1].threat_score if debates else 0.0}
    finally:
        db.close()


@router.get("/agents/status")
async def agent_status():
    db = SessionLocal()
    try:
        agents = ["SENTINEL", "FORGE", "NEMESIS", "BASTION", "ECHO", "COMMANDER"]
        status = {}
        for agent in agents:
            last_log = db.query(AgentLog).filter(AgentLog.agent_name == agent).order_by(AgentLog.timestamp.desc()).first()
            status[agent] = {
                "status": "active" if last_log else "idle",
                "last_action": last_log.action if last_log else None,
                "last_seen": last_log.timestamp.isoformat() if last_log else None,
                "total_executions": db.query(AgentLog).filter(AgentLog.agent_name == agent).count()
            }
        return {"agents": status}
    finally:
        db.close()


@router.get("/agents/llm-health")
async def llm_health():
    return llm_router.get_health_status()


# ==================== Canary Security Audit ====================

@router.get("/canary/audit")
async def canary_audit(status: Optional[str] = Query(None), limit: int = Query(100)):
    db = SessionLocal()
    try:
        query = db.query(CanaryEntry)
        if status: query = query.filter(CanaryEntry.status == status)
        canaries = query.order_by(CanaryEntry.created_at.desc()).limit(limit).all()
        return {
            "canaries": [c.to_dict() for c in canaries],
            "summary": {
                "total": db.query(CanaryEntry).count(),
                "dormant": db.query(CanaryEntry).filter(CanaryEntry.status == "dormant").count(),
                "triggered": db.query(CanaryEntry).filter(CanaryEntry.status == "triggered").count(),
                "neutralized": db.query(CanaryEntry).filter(CanaryEntry.status == "neutralized").count()
            }
        }
    finally:
        db.close()


@router.get("/canary/{mission_id}", response_model=CanaryStatusResponse)
async def canary_status(mission_id: UUID):
    result = execution_engine.check_canary_status(mission_id)
    return CanaryStatusResponse(mission_id=str(mission_id), security_posture=result["security_posture"], canaries=result["canaries"])


# ==================== Temporal Scrubbing ====================

@router.post("/temporal/query")
async def temporal_query(req: TemporalQuery):
    db = SessionLocal()
    try:
        start = datetime.fromisoformat(req.start_time) if req.start_time else datetime.min
        end = datetime.fromisoformat(req.end_time) if req.end_time else datetime.max
        missions = db.query(Mission).filter(Mission.created_at.between(start, end)).all()
        logs = db.query(AgentLog).filter(AgentLog.timestamp.between(start, end)).order_by(AgentLog.timestamp).all()
        spatial = db.query(SpatialEvent).filter(SpatialEvent.timestamp.between(start, end)).order_by(SpatialEvent.timestamp).all()
        timeline = []
        for m in missions: timeline.append({"type": "mission", "timestamp": m.created_at.isoformat(), "data": m.to_dict()})
        for log in logs: timeline.append({"type": "agent_log", "timestamp": log.timestamp.isoformat(), "data": log.to_dict()})
        for event in spatial: timeline.append({"type": "spatial_event", "timestamp": event.timestamp.isoformat(), "data": event.to_dict()})
        timeline.sort(key=lambda x: x["timestamp"])
        return {"time_range": {"start": start.isoformat(), "end": end.isoformat()}, "events": timeline, "event_count": len(timeline)}
    finally:
        db.close()


# ==================== Spatial Intelligence ====================

@router.post("/spatial/events")
async def create_spatial_event(req: SpatialEventRequest):
    db = SessionLocal()
    try:
        from geoalchemy2.shape import from_shape
        from shapely.geometry import Point
        wkt_element = f"SRID=4326;POINT({req.longitude} {req.latitude})"
        event = SpatialEvent(
            id=uuid4(), mission_id=UUID(req.mission_id) if req.mission_id else None,
            description=req.description, event_type=req.event_type,
            geolocation=wkt_element, metadata_=req.metadata or {}, timestamp=datetime.utcnow()
        )
        db.add(event)
        db.commit()
        return {"event_id": str(event.id), "status": "created", "location": {"lat": req.latitude, "lng": req.longitude}}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/spatial/events")
async def get_spatial_events(mission_id: Optional[UUID] = Query(None), event_type: Optional[str] = Query(None), limit: int = Query(200)):
    db = SessionLocal()
    try:
        query = db.query(SpatialEvent)
        if mission_id: query = query.filter(SpatialEvent.mission_id == mission_id)
        if event_type: query = query.filter(SpatialEvent.event_type == event_type)
        events = query.order_by(SpatialEvent.timestamp.desc()).limit(limit).all()
        return {"events": [e.to_dict() for e in events], "count": len(events)}
    finally:
        db.close()


@router.get("/spatial/heatmap")
async def spatial_heatmap(start_time: Optional[str] = Query(None), end_time: Optional[str] = Query(None)):
    db = SessionLocal()
    try:
        query = db.query(SpatialEvent)
        if start_time: query = query.filter(SpatialEvent.timestamp >= datetime.fromisoformat(start_time))
        if end_time: query = query.filter(SpatialEvent.timestamp <= datetime.fromisoformat(end_time))
        events = query.all()
        heatmap_points = []
        for event in events:
            if event.geolocation:
                heatmap_points.append({"location": str(event.geolocation), "timestamp": event.timestamp.isoformat(), "type": event.event_type})
        return {"points": heatmap_points, "density": len(heatmap_points), "time_range": {"start": start_time, "end": end_time}}
    finally:
        db.close()


# ==================== Webhook Execution Engine ====================

@router.post("/webhook/execute")
async def execute_webhook(req: WebhookRequest):
    """Execute a webhook to trigger real external actions."""
    result = await webhook_engine.execute_webhook(
        name=req.name, url=req.url, method=req.method, headers=req.headers, payload=req.payload
    )
    return result


@router.post("/email/send")
async def send_email(req: EmailRequest):
    """Send an email alert."""
    result = await webhook_engine.send_email(
        to=req.to, subject=req.subject, body=req.body, html=req.html, smtp_user=req.smtp_user, smtp_pass=req.smtp_pass
    )
    return result


@router.get("/webhook/stats")
async def webhook_stats():
    """Get webhook execution statistics."""
    return webhook_engine.get_stats()


@router.get("/webhook/log")
async def webhook_log(limit: int = Query(50)):
    """Get recent webhook execution log."""
    return webhook_engine.get_execution_log(limit)


# ==================== Data Fabric (Live Intelligence) ====================

@router.get("/intel/fetch")
async def fetch_intelligence():
    """Fetch live intelligence from all configured sources."""
    result = await data_fabric.fetch_intelligence()
    return result


@router.get("/intel/threats")
async def get_threat_intel():
    """Get current threat intelligence."""
    return {"threats": data_fabric.get_cached_intel(threat_only=True)}


@router.get("/intel/all")
async def get_all_intel():
    """Get all cached intelligence."""
    return {"intel": data_fabric.get_cached_intel(threat_only=False)}


# ==================== Digital Twin ====================

@router.post("/twin/entities")
async def add_twin_entity(req: TwinEntityRequest):
    """Add an entity to the digital twin."""
    entity = TwinEntity(
        id=req.id, entity_type=req.entity_type, name=req.name,
        attributes=req.attributes or {}, risk_score=req.risk_score
    )
    digital_twin.add_entity(entity)
    return {"status": "added", "entity_id": req.id}


@router.post("/twin/relationships")
async def add_relationship(req: TwinRelationship):
    """Add a relationship between two entities."""
    digital_twin.add_relationship(req.source_id, req.target_id, req.relationship, req.strength)
    return {"status": "added", "source": req.source_id, "target": req.target_id}


@router.get("/twin/network/{entity_id}")
async def get_entity_network(entity_id: str, max_depth: int = Query(2)):
    """Get the network surrounding an entity."""
    return digital_twin.get_entity_network(entity_id, max_depth)


@router.post("/twin/scenario")
async def run_scenario(req: ScenarioRequest):
    """Run a what-if simulation."""
    result = digital_twin.run_scenario(
        name=req.name, description=req.description,
        threat_entity_id=req.threat_entity_id, threat_severity=req.threat_severity,
        time_horizon_hours=req.time_horizon_hours
    )
    return {
        "scenario_id": result.scenario_id,
        "scenario_name": result.scenario_name,
        "risk_assessment": result.risk_assessment,
        "predicted_outcomes": result.predicted_outcomes[:20],
        "recommended_actions": result.recommended_actions,
    }


@router.get("/twin/scenarios")
async def get_scenarios(limit: int = Query(10)):
    """Get recent scenario results."""
    return digital_twin.get_all_scenarios(limit)


@router.get("/twin/scenarios/{scenario_id}")
async def get_scenario_detail(scenario_id: str):
    """Get full details of a scenario."""
    detail = digital_twin.get_scenario_detail(scenario_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return detail


@router.get("/twin/stats")
async def get_twin_stats():
    """Get digital twin graph statistics."""
    return digital_twin.get_graph_stats()


# ==================== System Health ====================

@router.get("/health")
async def health():
    db_health = await health_check()
    return {
        "status": "nominal", "database": db_health,
        "mode": "ADVERSARIAL_WORKFLOW_ACTIVE", "version": "3.0.0-PRODUCTION",
        "llm_providers": llm_router.get_health_status(),
        "websocket": websocket_manager.get_stats(),
        "webhooks": webhook_engine.get_stats(),
    }


@router.post("/seed")
async def seed_database():
    """
    Endpoint to populate the database with 500+ synthetic entities and missions.
    Run this once after deployment to initialize the platform with demo data.
    """
    try:
        from src.data.seed_data import seed_database as run_seed
        run_seed()
        return {"status": "success", "message": "Database seeded successfully with demo data."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")


@router.get("/ping")
async def ping():
    return {"status": "AEGIS ONLINE", "mode": "ADVERSARIAL_WORKFLOW_ACTIVE", "version": "3.0.0-PRODUCTION", "timestamp": datetime.utcnow().isoformat()}


# ==================== Palantir-Style COP Endpoints ====================

@router.get("/dashboard/spatial-grid")
async def spatial_grid():
    """Full GeoJSON FeatureCollection of all geospatial threats and assets."""
    db = SessionLocal()
    try:
        events = db.query(SpatialEvent).order_by(SpatialEvent.timestamp.desc()).limit(500).all()
        features = []
        for e in events:
            lat, lon = None, None
            # Extract from metadata first
            if e.metadata_:
                lat = e.metadata_.get("latitude")
                lon = e.metadata_.get("longitude")
            # Fallback: parse WKBElement from geolocation column
            if not lat or not lon:
                try:
                    from geoalchemy2.shape import to_shape
                    geom = to_shape(e.geolocation)
                    lon, lat = geom.x, geom.y
                except:
                    pass
            if lat and lon:
                meta = dict(e.metadata_ or {})
                meta["latitude"] = lat
                meta["longitude"] = lon
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "properties": {
                        "id": str(e.id),
                        "description": e.description,
                        "event_type": e.event_type,
                        "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                        "metadata": meta,
                    }
                })
        return {
            "type": "FeatureCollection",
            "features": features,
            "total": len(features),
            "generated_at": datetime.utcnow().isoformat(),
        }
    finally:
        db.close()


@router.get("/dashboard/actions")
async def dashboard_actions():
    """Structured list of active missions with plans and canary states."""
    db = SessionLocal()
    try:
        missions = db.query(Mission).order_by(Mission.created_at.desc()).all()
        result = []
        for m in missions:
            canaries = db.query(CanaryEntry).filter(CanaryEntry.mission_id == m.id).all()
            actions = db.query(AgentAction).filter(AgentAction.mission_id == m.id).order_by(AgentAction.timestamp.desc()).limit(10).all()
            result.append({
                "mission_id": str(m.id),
                "name": m.name,
                "status": m.status,
                "threat_score": m.threat_score,
                "stress_test_score": m.stress_test_score,
                "overt_plan": (m.overt_plan or "")[:300],
                "covert_plan": "[ENCRYPTED]" if m.covert_plan else "N/A",
                "contingency_plan": (m.contingency_plan or "")[:300],
                "canary_state": {
                    "total": len(canaries),
                    "dormant": len([c for c in canaries if c.status == "dormant"]),
                    "triggered": len([c for c in canaries if c.status == "triggered"]),
                    "neutralized": len([c for c in canaries if c.status == "neutralized"]),
                },
                "recent_actions": [{"agent": a.agent_name, "type": a.action_type, "title": a.title, "severity": a.severity, "timestamp": a.timestamp.isoformat() if a.timestamp else None} for a in actions],
                "created_at": m.created_at.isoformat() if m.created_at else None,
            })
        return {"missions": result, "total": len(result), "timestamp": datetime.utcnow().isoformat()}
    finally:
        db.close()


@router.get("/dashboard/intel-feed")
async def intel_feed(limit: int = Query(50)):
    """Latest intel reports with metadata for vector-searchable intelligence."""
    db = SessionLocal()
    try:
        reports = db.query(IntelReport).order_by(IntelReport.created_at.desc()).limit(limit).all()
        return {
            "reports": [
                {
                    "id": str(r.id),
                    "content": r.content[:500],
                    "source_type": r.metadata_.get("source_type", "unknown") if r.metadata_ else "unknown",
                    "threat_actor": r.metadata_.get("threat_actor", "unknown") if r.metadata_ else "unknown",
                    "location": r.metadata_.get("location", "unknown") if r.metadata_ else "unknown",
                    "confidence": r.metadata_.get("confidence", "unknown") if r.metadata_ else "unknown",
                    "classification": r.metadata_.get("classification", "UNCLASSIFIED") if r.metadata_ else "UNCLASSIFIED",
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in reports
            ],
            "total": len(reports),
            "timestamp": datetime.utcnow().isoformat(),
        }
    finally:
        db.close()

"""
AEGIS Database Models
Comprehensive schema for missions, task trees, canaries, intel, and spatial events.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, JSON, Text, Boolean,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import uuid
from datetime import datetime

Base = declarative_base()


class Mission(Base):
    """Core mission record tracking strategic directives and execution state."""
    __tablename__ = "missions"
    __table_args__ = (
        Index("idx_mission_status", "status"),
        Index("idx_mission_created", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    directive = Column(Text, nullable=True)
    status = Column(String(50), default="planning")  # planning, executing, completed, aborted

    # Three execution paths
    overt_plan = Column(Text, nullable=True)
    covert_plan = Column(Text, nullable=True)
    contingency_plan = Column(Text, nullable=True)

    # Scoring & intelligence
    threat_score = Column(Float, default=0.0)
    stress_test_score = Column(Float, default=0.0)
    intel_summary = Column(Text, nullable=True)
    debate_log = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    canaries = relationship("CanaryEntry", back_populates="mission", cascade="all, delete-orphan")
    task_trees = relationship("TaskTree", back_populates="mission", cascade="all, delete-orphan")
    intel_reports = relationship("IntelReport", back_populates="mission", cascade="all, delete-orphan")
    agent_actions = relationship("AgentAction", back_populates="mission", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "directive": self.directive,
            "status": self.status,
            "threat_score": self.threat_score,
            "stress_test_score": self.stress_test_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TaskTree(Base):
    """Represents one of three task trees (overt/covert/contingency) for a mission."""
    __tablename__ = "task_trees"
    __table_args__ = (
        Index("idx_task_tree_mission", "mission_id"),
        Index("idx_task_tree_type", "tree_type"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=False)
    tree_type = Column(String(50), nullable=False)  # overt, covert, contingency
    root_node_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    mission = relationship("Mission", back_populates="task_trees")
    nodes = relationship("TaskTreeNode", back_populates="tree", cascade="all, delete-orphan")


class TaskTreeNode(Base):
    """Individual task node within a task tree."""
    __tablename__ = "task_tree_nodes"
    __table_args__ = (
        Index("idx_node_tree", "tree_id"),
        Index("idx_node_status", "status"),
    )

    id = Column(String(255), primary_key=True)
    tree_id = Column(UUID(as_uuid=True), ForeignKey("task_trees.id"), nullable=False)
    parent_id = Column(String(255), nullable=True)
    task_description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(50), default="pending")  # pending, active, completed, blocked, dormant
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tree = relationship("TaskTree", back_populates="nodes")


class CanaryEntry(Base):
    """Canary entries for security audit and leak detection."""
    __tablename__ = "canaries"
    __table_args__ = (
        Index("idx_canary_mission", "mission_id"),
        Index("idx_canary_status", "status"),
        UniqueConstraint("payload_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=False)
    tool_type = Column(String(50))  # calendar, task, notes
    payload_id = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), default="dormant")  # dormant, triggered, neutralized
    triggered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    mission = relationship("Mission", back_populates="canaries")

    def to_dict(self):
        return {
            "id": str(self.id),
            "mission_id": str(self.mission_id),
            "tool_type": self.tool_type,
            "payload_id": self.payload_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
        }


class IntelReport(Base):
    """Intelligence reports with vector embeddings for semantic search."""
    __tablename__ = "intel_reports"
    __table_args__ = (
        Index("idx_intel_created", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))  # Gemini embedding dimension
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    mission = relationship("Mission", back_populates="intel_reports")

    def to_dict(self):
        return {
            "id": str(self.id),
            "mission_id": str(self.mission_id) if self.mission_id else None,
            "content": self.content[:500],  # Truncate for list views
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SpatialEvent(Base):
    """Geospatial events tracked on the spatial-temporal grid."""
    __tablename__ = "spatial_events"
    __table_args__ = (
        Index("idx_spatial_time", "timestamp"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=True)
    description = Column(String(500), nullable=False)
    event_type = Column(String(100), nullable=True)  # resource_movement, vulnerability, operation
    geolocation = Column(Geometry('POINT', srid=4326))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata_ = Column("metadata", JSON, nullable=True)

    def to_dict(self):
        # Extract lat/lon from WKBElement using geoalchemy2.shape
        lat, lon = None, None
        if self.geolocation:
            try:
                shape = to_shape(self.geolocation)
                lon, lat = shape.x, shape.y
            except Exception:
                pass
        
        meta = dict(self.metadata_ or {})
        if lat is not None:
            meta["latitude"] = lat
        if lon is not None:
            meta["longitude"] = lon
            
        return {
            "id": str(self.id),
            "description": self.description,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": meta,
        }


class AgentLog(Base):
    """Structured agent execution logs for audit and UI display."""
    __tablename__ = "agent_logs"
    __table_args__ = (
        Index("idx_log_mission", "mission_id"),
        Index("idx_log_agent", "agent_name"),
        Index("idx_log_timestamp", "timestamp"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=True)
    agent_name = Column(String(50), nullable=False)  # SENTINEL, FORGE, NEMESIS, BASTION, ECHO, COMMANDER
    action = Column(String(100), nullable=False)
    result = Column(String(500), nullable=True)
    log_metadata = Column("log_metadata", JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": str(self.id),
            "mission_id": str(self.mission_id) if self.mission_id else None,
            "agent": self.agent_name,
            "action": self.action,
            "result": self.result,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class AgentAction(Base):
    """
    Concrete, viewable actions performed by agents.
    Each action has type, status, details, and evidence.
    """
    __tablename__ = "agent_actions"
    __table_args__ = (
        Index("idx_action_mission", "mission_id"),
        Index("idx_action_agent", "agent_name"),
        Index("idx_action_type", "action_type"),
        Index("idx_action_status", "status"),
        Index("idx_action_timestamp", "timestamp"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=False)
    agent_name = Column(String(50), nullable=False)
    action_type = Column(String(100), nullable=False)  # e.g., "threat_detected", "task_created", "canary_deployed"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)  # Supporting data (task IDs, canary IDs, etc.)
    severity = Column(String(20), default="info")  # info, low, medium, high, critical
    status = Column(String(50), default="completed")  # pending, in_progress, completed, failed
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    mission = relationship("Mission", back_populates="agent_actions")

    def to_dict(self):
        return {
            "id": str(self.id),
            "mission_id": str(self.mission_id),
            "agent": self.agent_name,
            "action_type": self.action_type,
            "title": self.title,
            "description": self.description,
            "details": self.details,
            "evidence": self.evidence,
            "severity": self.severity,
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class DebateRound(Base):
    """Records of NEMESIS-BASTION adversarial debate rounds."""
    __tablename__ = "debate_rounds"
    __table_args__ = (
        Index("idx_debate_mission", "mission_id"),
        Index("idx_debate_round", "round_number"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    nemesis_analysis = Column(Text, nullable=False)
    bastion_response = Column(Text, nullable=False)
    threat_score = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": str(self.id),
            "mission_id": str(self.mission_id),
            "round": self.round_number,
            "nemesis_analysis": self.nemesis_analysis,
            "bastion_response": self.bastion_response,
            "threat_score": self.threat_score,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

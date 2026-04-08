"""
AEGIS Digital Twin Simulator
What-if scenario modeling with predictive analytics.
"""

import json
import logging
import networkx as nx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import uuid4
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("aegis.digital_twin")


@dataclass
class TwinEntity:
    """A real-world entity in the digital twin."""
    id: str
    entity_type: str  # person, asset, location, threat, mission
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ScenarioResult:
    """Result of a what-if simulation."""
    scenario_id: str
    scenario_name: str
    description: str
    inputs: Dict[str, Any]
    predicted_outcomes: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    recommended_actions: List[str]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class DigitalTwinSimulator:
    """
    Creates a virtual representation of the operational environment.
    Runs what-if simulations and predicts outcomes.
    """

    def __init__(self):
        self.graph = nx.DiGraph()  # Entity relationship graph
        self.entities: Dict[str, TwinEntity] = {}
        self.scenario_history: List[ScenarioResult] = []
        self.threat_patterns: List[Dict[str, Any]] = []

    def add_entity(self, entity: TwinEntity):
        """Add an entity to the digital twin."""
        self.entities[entity.id] = entity
        self.graph.add_node(entity.id, **entity.attributes, entity_type=entity.entity_type)

    def add_relationship(self, source_id: str, target_id: str, relationship: str, strength: float = 1.0):
        """Define a relationship between two entities."""
        self.graph.add_edge(source_id, target_id, relationship=relationship, strength=strength)

    def remove_entity(self, entity_id: str):
        """Remove an entity from the digital twin."""
        if entity_id in self.entities:
            del self.entities[entity_id]
            if entity_id in self.graph:
                self.graph.remove_node(entity_id)

    def get_entity_network(self, entity_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """Get the network surrounding an entity."""
        if entity_id not in self.graph:
            return {"error": "Entity not found"}

        ego_graph = nx.ego_graph(self.graph, entity_id, radius=max_depth)
        nodes = []
        for node_id, attrs in ego_graph.nodes(data=True):
            entity = self.entities.get(node_id)
            nodes.append({
                "id": node_id,
                "type": attrs.get("entity_type", "unknown"),
                "name": entity.name if entity else node_id,
                "risk_score": entity.risk_score if entity else 0,
                "attributes": attrs,
            })

        edges = []
        for src, tgt, attrs in ego_graph.edges(data=True):
            edges.append({
                "source": src,
                "target": tgt,
                "relationship": attrs.get("relationship", "unknown"),
                "strength": attrs.get("strength", 1.0),
            })

        return {"nodes": nodes, "edges": edges, "center": entity_id}

    def run_scenario(
        self,
        name: str,
        description: str,
        threat_entity_id: str,
        threat_severity: float,
        time_horizon_hours: int = 24,
    ) -> ScenarioResult:
        """
        Run a what-if simulation.
        Predicts how a threat propagates through the network.
        """
        if threat_entity_id not in self.graph:
            return ScenarioResult(
                scenario_id=str(uuid4()),
                scenario_name=name,
                description=description,
                inputs={"threat_entity": threat_entity_id, "severity": threat_severity},
                predicted_outcomes=[{"error": "Threat entity not in graph"}],
                risk_assessment={"overall_risk": 0},
                recommended_actions=[],
            )

        # Predict threat propagation
        affected_entities = []
        risk_scores = {}

        # BFS from threat entity
        for node in nx.single_source_shortest_path(self.graph, threat_entity_id):
            entity = self.entities.get(node)
            if entity and node != threat_entity_id:
                distance = nx.shortest_path_length(self.graph, threat_entity_id, node)
                propagated_risk = threat_severity * (0.7 ** distance)
                risk_scores[node] = propagated_risk
                affected_entities.append({
                    "entity_id": node,
                    "entity_name": entity.name,
                    "entity_type": entity.entity_type,
                    "distance_from_threat": distance,
                    "predicted_risk_score": round(propagated_risk, 3),
                    "time_to_impact_hours": round(distance * 2, 1),
                })

        # Sort by risk
        affected_entities.sort(key=lambda x: x["predicted_risk_score"], reverse=True)

        # Overall risk assessment
        max_risk = max([e["predicted_risk_score"] for e in affected_entities], default=0)
        avg_risk = sum([e["predicted_risk_score"] for e in affected_entities]) / max(len(affected_entities), 1)

        # Generate recommended actions
        actions = []
        if max_risk > 0.7:
            actions.append("CRITICAL: Immediate containment required for high-risk entities")
            actions.append("Isolate affected network segments")
            actions.append("Notify security operations center")
        elif max_risk > 0.4:
            actions.append("ELEVATED: Enhanced monitoring required")
            actions.append("Review access controls for affected entities")
            actions.append("Prepare incident response team")
        else:
            actions.append("MONITOR: Continue standard surveillance")
            actions.append("Log threat indicators for future analysis")

        result = ScenarioResult(
            scenario_id=str(uuid4()),
            scenario_name=name,
            description=description,
            inputs={
                "threat_entity": threat_entity_id,
                "threat_severity": threat_severity,
                "time_horizon_hours": time_horizon_hours,
            },
            predicted_outcomes=affected_entities,
            risk_assessment={
                "overall_risk": round(max_risk, 3),
                "average_risk": round(avg_risk, 3),
                "affected_entity_count": len(affected_entities),
                "critical_entities": [e for e in affected_entities if e["predicted_risk_score"] > 0.7],
                "time_to_first_impact": affected_entities[0]["time_to_impact_hours"] if affected_entities else 0,
            },
            recommended_actions=actions,
        )

        self.scenario_history.append(result)
        logger.info(f"Digital Twin Scenario '{name}': {len(affected_entities)} affected, risk={max_risk:.2f}")

        return result

    def get_all_scenarios(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent scenario results."""
        return [
            {
                "scenario_id": s.scenario_id,
                "scenario_name": s.scenario_name,
                "description": s.description,
                "risk_assessment": s.risk_assessment,
                "affected_count": len(s.predicted_outcomes),
                "timestamp": s.timestamp,
            }
            for s in reversed(self.scenario_history[-limit:])
        ]

    def get_scenario_detail(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get full details of a scenario."""
        for s in self.scenario_history:
            if s.scenario_id == scenario_id:
                return {
                    "scenario_id": s.scenario_id,
                    "scenario_name": s.scenario_name,
                    "description": s.description,
                    "inputs": s.inputs,
                    "predicted_outcomes": s.predicted_outcomes,
                    "risk_assessment": s.risk_assessment,
                    "recommended_actions": s.recommended_actions,
                    "timestamp": s.timestamp,
                }
        return None

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the entity graph."""
        if not self.graph.nodes:
            return {"total_entities": 0, "total_relationships": 0}

        return {
            "total_entities": self.graph.number_of_nodes(),
            "total_relationships": self.graph.number_of_edges(),
            "entity_types": dict(nx.get_node_attributes(self.graph, "entity_type")),
            "is_connected": nx.is_weakly_connected(self.graph),
            "average_degree": round(sum(dict(self.graph.degree()).values()) / max(self.graph.number_of_nodes(), 1), 2),
        }


# Global instance
digital_twin = DigitalTwinSimulator()

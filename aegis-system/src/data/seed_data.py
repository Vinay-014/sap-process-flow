"""
AEGIS Massive Synthetic Data Seed Script
Generates 500+ realistic military + supply chain entities for PostgreSQL.
All data is synthetic but structurally identical to classified/corporate data.
"""

import sys, os, random
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from uuid import uuid4
from src.db.session import SessionLocal
from src.db.models import Mission, CanaryEntry, IntelReport, SpatialEvent, AgentAction, AgentLog

logger = logging.getLogger("aegis.seed_data")

# ==================== Strategic Zones ====================
STRATEGIC_ZONES = [
    {"name": "South China Sea", "lat": 12.0, "lon": 115.0, "radius": 8},
    {"name": "Strait of Hormuz", "lat": 26.5, "lon": 56.0, "radius": 2},
    {"name": "Black Sea", "lat": 44.0, "lon": 34.0, "radius": 4},
    {"name": "Baltic Sea", "lat": 57.0, "lon": 19.0, "radius": 3},
    {"name": "Indo-Pacific Corridor", "lat": 5.0, "lon": 105.0, "radius": 12},
    {"name": "Eastern Europe Forward", "lat": 50.5, "lon": 30.0, "radius": 5},
    {"name": "Mediterranean Chokepoint", "lat": 35.0, "lon": 18.0, "radius": 3},
    {"name": "Pacific Island Chain", "lat": 8.0, "lon": 135.0, "radius": 10},
]

# ==================== Supply Chain Nodes ====================
PORTS = [
    ("Port of Shanghai", 31.23, 121.47, "China", "critical"),
    ("Port of Singapore", 1.26, 103.85, "Singapore", "critical"),
    ("Port of Rotterdam", 51.92, 4.48, "Netherlands", "critical"),
    ("Port of Jebel Ali", 25.01, 55.05, "UAE", "high"),
    ("Port of Los Angeles", 33.74, -118.27, "USA", "critical"),
    ("Port of Hamburg", 53.55, 9.99, "Germany", "high"),
    ("Port of Busan", 35.18, 129.08, "South Korea", "high"),
    ("Port of Mumbai", 18.94, 72.88, "India", "medium"),
    ("Port of Durban", -29.86, 31.02, "South Africa", "medium"),
    ("Port of Santos", -23.96, -46.33, "Brazil", "medium"),
    ("Port of Felixstowe", 51.96, 1.35, "UK", "high"),
    ("Port of Long Beach", 33.77, -118.19, "USA", "critical"),
    ("Port of Kaohsiung", 22.63, 120.30, "Taiwan", "critical"),
    ("Port of Piraeus", 37.95, 23.65, "Greece", "high"),
    ("Port of Odessa", 46.49, 30.73, "Ukraine", "high"),
]

# ==================== Military Units ====================
MILITARY_UNITS = [
    ("US 7th Fleet - Forward", 35.44, 139.64, "naval", "active"),
    ("NATO Enhanced Forward Presence", 54.68, 25.28, "ground", "active"),
    ("INDOPACOM Strike Group", 13.75, 121.05, "naval", "deployed"),
    ("USAFE Air Wing", 49.78, 9.18, "air", "active"),
    ("Carrier Strike Group 5", 22.28, 114.16, "naval", "transit"),
    ("Amphibious Ready Group", 19.07, 72.87, "naval", "deployed"),
    ("Strategic Bomber Task Force", 33.66, 130.42, "air", "standby"),
    ("Submarine Force Pacific", 21.31, 157.80, "naval", "active"),
]

# ==================== Threat Actors ====================
THREAT_ACTORS = [
    ("APT-Corvus", "state-sponsored", "cyber", 0.85),
    ("Naval Intrusion Unit-Alpha", "non-state", "maritime", 0.72),
    ("Supply Chain Interceptor", "criminal", "logistics", 0.65),
    ("Cyber Espionage Group 12", "state-sponsored", "cyber", 0.90),
    ("Maritime Militia Fleet", "state-affiliated", "maritime", 0.78),
    ("Insider Threat Network", "internal", "infiltration", 0.55),
    ("Smuggling Syndicate Omega", "criminal", "logistics", 0.60),
    ("Reconnaissance Drone Swarm", "state-sponsored", "surveillance", 0.82),
]

# ==================== Intel Content Templates ====================
INTEL_TEMPLATES = {
    "SIGINT": [
        "Intercepted communications between {actor} and forward operating base at {location}. Signal strength indicates active coordination for upcoming operation.",
        "SIGINT collection at {location} reveals increased radio traffic from {actor}. Pattern analysis suggests preparation for {operation_type} within 72 hours.",
        "Electronic warfare signatures detected near {location}. {actor} deploying jamming equipment consistent with {operation_type} operations.",
        "Signals intelligence indicates {actor} has established new C2 node at {location}. Frequency hopping pattern suggests advanced encryption capabilities.",
    ],
    "HUMINT": [
        "Human source reports {actor} personnel observed conducting reconnaissance of {location}. Activity consistent with pre-operational surveillance.",
        "Confidential informant indicates {actor} recruiting local assets at {location} for intelligence gathering on {operation_type} operations.",
        "Defector provides intelligence on {actor} operational planning. Target: {location}. Timeline: {timeline}. Method: {operation_type}.",
        "Local asset reports unusual activity by {actor} at {location}. Increased vehicle movements and communications intercepts suggest imminent {operation_type}.",
    ],
    "OSINT": [
        "Open source analysis reveals {actor} shipping manifests correlating with {operation_type} equipment deliveries to {location}. Satellite imagery confirms facility expansion.",
        "Social media and commercial satellite data indicate {actor} establishing new infrastructure at {location}. Construction patterns consistent with {operation_type} capabilities.",
        "Commercial vessel tracking shows unusual patterns near {location}. AIS transponder gaps correlate with known {actor} operational areas.",
        "News media and public records analysis reveals {actor} front companies operating near {location}. Corporate registries show connections to known {operation_type} networks.",
    ],
    "CYBER": [
        "Cyber threat intelligence: {actor} deploying new malware variant targeting {operation_type} systems. IOCs indicate targeting of infrastructure at {location}.",
        "Network intrusion detected at {location}. Attack attribution points to {actor}. Exfiltration of {operation_type} data confirmed.",
        "Phishing campaign attributed to {actor} targeting personnel at {location}. Payload analysis reveals {operation_type} intelligence collection capability.",
        "Zero-day exploit chain identified in {operation_type} systems. Attribution assessment: {actor} with {confidence_level} confidence. Patch deployment urgent.",
    ],
}

OPERATION_TYPES = ["cyber strike", "maritime blockade", "supply chain disruption", "electronic warfare", "intelligence gathering", "force projection", "covert insertion", "economic coercion"]
TIMELINES = ["72 hours", "7-14 days", "30 days", "imminent", "Q2 2026", "Q3 2026"]

# ==================== Risk Indicators ====================
SUPPLY_RISKS = [
    ("Port Congestion Alert", "logistics", "high"),
    ("Geopolitical Sanctions Risk", "geopolitical", "critical"),
    ("Container Shortage Warning", "logistics", "medium"),
    ("Piracy Activity Increase", "maritime", "high"),
    ("Customs Delay Escalation", "regulatory", "medium"),
    ("Route Disruption - Canal Closure", "logistics", "critical"),
    ("Cyber Attack on Port Systems", "cyber", "high"),
    ("Weather Disruption - Typhoon Season", "environmental", "medium"),
    ("Trade Restriction Warning", "geopolitical", "high"),
    ("Fuel Price Volatility", "economic", "medium"),
]

# ==================== Mission Templates ====================
MISSIONS = [
    {
        "name": "OP IRON SHIELD",
        "directive": "Detect and neutralize insider threat: Suspected employee leaking Q3 acquisition plans to competitor Apex Corp. Deploy canary tokens across all shared systems. Monitor calendar anomalies and document access patterns. Generate comprehensive threat assessment with overt, covert, and contingency response plans.",
        "status": "executing",
        "threat": 0.72,
        "stress": 0.65,
    },
    {
        "name": "SUPPLY CHAIN DEFENSE ALPHA",
        "directive": "Monitor critical supply chain nodes across Indo-Pacific corridor. Track vessel movements, port congestion, and geopolitical risk indicators. Establish early warning system for disruptions to semiconductor and rare earth mineral supply chains.",
        "status": "executing",
        "threat": 0.58,
        "stress": 0.52,
    },
    {
        "name": "OP MARITIME SENTINEL",
        "directive": "Conduct persistent ISR over South China Sea shipping lanes. Monitor maritime militia activity, track unauthorized vessel movements near disputed features, and maintain real-time awareness of naval force posture. Report anomalies to fleet command.",
        "status": "executing",
        "threat": 0.81,
        "stress": 0.74,
    },
    {
        "name": "CYBER SHIELD DEFENSE",
        "directive": "Hunt for advanced persistent threats targeting critical infrastructure. Deploy network sensors, analyze threat intelligence feeds, and coordinate with allied cyber defense teams. Prepare incident response playbooks for state-sponsored cyber operations.",
        "status": "executing",
        "threat": 0.90,
        "stress": 0.85,
    },
    {
        "name": "OP FORWARD RESOLVE",
        "directive": "Assess and enhance forward-deployed force protection posture in Eastern Europe. Monitor adversary military exercises, track equipment movements, and evaluate logistics readiness. Coordinate with NATO partners on collective defense posture.",
        "status": "planning",
        "threat": 0.65,
        "stress": 0.60,
    },
    {
        "name": "GLOBAL TRADE GUARDIAN",
        "directive": "Establish comprehensive supply chain resilience monitoring across 15 critical ports. Deploy predictive analytics for disruption forecasting, monitor geopolitical risk indicators, and maintain alternative routing options for critical commodities.",
        "status": "executing",
        "threat": 0.45,
        "stress": 0.40,
    },
    {
        "name": "OP SILENT WATCHER",
        "directive": "Conduct signals intelligence collection on adversary communications networks. Map command and control infrastructure, identify key nodes in threat actor networks, and provide targeting-quality intelligence to operational commanders.",
        "status": "executing",
        "threat": 0.88,
        "stress": 0.80,
    },
    {
        "name": "CRITICAL INFRASTRUCTURE SHIELD",
        "directive": "Assess vulnerabilities in national critical infrastructure sectors: energy, water, telecommunications, and financial services. Coordinate with sector-specific agencies to harden defenses against state-sponsored and criminal threat actors.",
        "status": "planning",
        "threat": 0.70,
        "stress": 0.62,
    },
    {
        "name": "OP RAPID RESPONSE",
        "directive": "Maintain rapid response capability for emerging crises in the Indo-Pacific region. Pre-position logistics, establish communication protocols with allied forces, and develop contingency plans for multiple crisis scenarios including natural disasters, military escalation, and humanitarian emergencies.",
        "status": "executing",
        "threat": 0.55,
        "stress": 0.48,
    },
    {
        "name": "INFORMATION OPERATIONS DEFENSE",
        "directive": "Detect, attribute, and counter adversarial information operations targeting democratic institutions. Monitor social media manipulation campaigns, track coordinated inauthentic behavior, and develop counter-narrative strategies to protect public discourse.",
        "status": "planning",
        "threat": 0.62,
        "stress": 0.55,
    },
]


def random_zone():
    zone = random.choice(STRATEGIC_ZONES)
    return (
        round(zone["lat"] + random.uniform(-zone["radius"], zone["radius"]), 4),
        round(zone["lon"] + random.uniform(-zone["radius"], zone["radius"]), 4),
        zone["name"]
    )


def generate_intel_content(actor, location):
    source_type = random.choice(list(INTEL_TEMPLATES.keys()))
    template = random.choice(INTEL_TEMPLATES[source_type])
    content = template.format(
        actor=actor,
        location=location,
        operation_type=random.choice(OPERATION_TYPES),
        timeline=random.choice(TIMELINES),
        confidence_level=random.choice(["HIGH", "MEDIUM-HIGH", "MEDIUM"]),
    )
    return source_type, content


def seed_database():
    """
    Seeds the database with 500+ synthetic entities.
    Designed to run automatically on fresh deployments or manually via API.
    """
    db = SessionLocal()
    count = 0

    try:
        print_header("AEGIS DATA SEED: Generating 500+ synthetic entities")

        # 1. Seed 10 missions
        print_step(1, "Seeding missions...")
        mission_objs = []
        for m in MISSIONS:
            mission = Mission(
                id=uuid4(),
                name=m["name"],
                directive=m["directive"],
                status=m["status"],
                threat_score=m["threat"],
                stress_test_score=m["stress"],
                overt_plan=f"OVERT: Deploy {random.choice(OPERATION_TYPES)} monitoring protocols across designated sectors. Establish communication links with allied command centers.",
                covert_plan=f"COVERT: Classified intelligence collection operations targeting {random.choice(THREAT_ACTORS)[0]} C2 infrastructure. Access restricted to TS/SCI clearance.",
                contingency_plan=f"CONTINGENCY: Activate rapid response protocol if threat score exceeds 0.70. Pre-positioned assets at {random.choice(STRATEGIC_ZONES)['name']} will transition to active status.",
                intel_summary=f"Intel summary for {m['name']}: {random.randint(5,25)} threat indicators identified across {random.randint(3,8)} intelligence disciplines. Assessment ongoing.",
                created_at=datetime.utcnow() - timedelta(days=random.randint(0,30)),
                updated_at=datetime.utcnow() - timedelta(days=random.randint(0,5)),
            )
            db.add(mission)
            mission_objs.append(mission)
        
        db.flush()

        # 2. Seed 120+ Spatial Events (Military + Supply Chain)
        print_step(2, "Seeding geospatial events...")
        for i in range(120):
            lat, lon, zone = random_zone()
            if i < 50:  # Military events
                unit = random.choice(MILITARY_UNITS)
                event = SpatialEvent(
                    id=uuid4(),
                    mission_id=random.choice(mission_objs).id,
                    description=f"{unit[0]} — {random.choice(['patrol complete', 'position shift', 'anomaly detected', 'routine surveillance', 'force movement'])} in {zone}",
                    event_type=random.choice(["force_movement", "patrol_route", "surveillance", "anomaly", "exercise"]),
                    geolocation=f"SRID=4326;POINT({lon} {lat})",
                    timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 720)),
                    metadata_={"unit": unit[0], "unit_type": unit[2], "status": unit[3], "zone": zone},
                )
            else:  # Supply chain events
                port = random.choice(PORTS)
                risk = random.choice(SUPPLY_RISKS)
                event = SpatialEvent(
                    id=uuid4(),
                    mission_id=random.choice(mission_objs).id,
                    description=f"{port[0]} — {risk[0]}: {random.choice(['Vessel queue: ' + str(random.randint(5,50)), 'Delay: ' + str(random.randint(1,14)) + ' days', 'Throughput: ' + str(random.randint(60,100)) + '%', 'Status: ' + risk[2].upper()])}",
                    event_type=random.choice(["port_congestion", "vessel_tracking", "supply_disruption", "risk_indicator", "logistics_node"]),
                    geolocation=f"SRID=4326;POINT({port[2]} {port[1]})",
                    timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 720)),
                    metadata_={"port": port[0], "country": port[3], "priority": port[4], "risk_type": risk[0], "risk_level": risk[2]},
                )
            db.add(event)
        count += 120

        # 3. Seed 100+ Intel Reports
        print_step(3, "Seeding intel reports...")
        for i in range(100):
            actor = random.choice(THREAT_ACTORS)[0]
            zone = random.choice(STRATEGIC_ZONES)["name"]
            source_type, content = generate_intel_content(actor, zone)
            report = IntelReport(
                id=uuid4(),
                mission_id=random.choice(mission_objs).id,
                content=content,
                metadata_={
                    "source_type": source_type,
                    "threat_actor": actor,
                    "location": zone,
                    "confidence": random.choice(["HIGH", "MEDIUM", "LOW"]),
                    "classification": random.choice(["SECRET", "TS//SI", "UNCLASSIFIED//FOUO"]),
                    "analyst": f"Analyst-{random.randint(1,50):03d}",
                },
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 720)),
            )
            db.add(report)
        count += 100

        # 4. Seed 150+ Canary Entries
        print_step(4, "Seeding canary entries...")
        canary_types = ["calendar", "task", "notes", "email", "document", "api_endpoint"]
        for i in range(150):
            canary = CanaryEntry(
                id=uuid4(),
                mission_id=random.choice(mission_objs).id,
                tool_type=random.choice(canary_types),
                payload_id=f"AEGIS_{uuid4().hex[:12]}",
                status=random.choices(["dormant", "triggered", "neutralized"], weights=[80, 15, 5])[0],
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 720)),
            )
            db.add(canary)
        count += 150

        # 5. Seed 80+ Agent Actions
        print_step(5, "Seeding agent actions...")
        agents = ["SENTINEL", "FORGE", "NEMESIS", "BASTION", "ECHO", "COMMANDER"]
        action_types = [
            ("threat_detected", "high", "Threat indicator identified"),
            ("canary_deployed", "medium", "Canary token deployed"),
            ("task_created", "high", "Operational task created"),
            ("vulnerability_assessment", "medium", "Vulnerability scan completed"),
            ("defense_playbook_deployed", "high", "Defensive measures activated"),
            ("operational_order_issued", "critical", "Command directive issued"),
            ("intel_gathered", "low", "Intelligence collected"),
            ("asset_monitored", "info", "Asset under surveillance"),
            ("alert_escalated", "high", "Threat alert escalated to command"),
            ("countermeasure_active", "medium", "Defensive countermeasure engaged"),
        ]
        for i in range(80):
            agent = random.choice(agents)
            atype, severity, desc = random.choice(action_types)
            mission = random.choice(mission_objs)
            action = AgentAction(
                id=uuid4(),
                mission_id=mission.id,
                agent_name=agent,
                action_type=atype,
                title=f"{agent}: {desc} — {mission.name}",
                description=f"Agent {agent} executed {atype} action for {mission.name}. Severity: {severity}. Details: {random.choice(OPERATION_TYPES)} operation at {random.choice(STRATEGIC_ZONES)['name']}. Status: {'completed' if random.random() > 0.1 else 'in_progress'}.",
                details={"agent": agent, "action_type": atype, "mission": mission.name},
                evidence={"evidence_id": f"EVD-{uuid4().hex[:8]}", "source": random.choice(["automated_scan", "analyst_report", "sensor_data", "intercept"])},
                severity=severity,
                status="completed",
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 720)),
            )
            db.add(action)
        count += 80

        # 6. Seed 60+ Agent Logs
        print_step(6, "Seeding agent logs...")
        for i in range(60):
            agent = random.choice(agents)
            log = AgentLog(
                id=uuid4(),
                mission_id=random.choice(mission_objs).id,
                agent_name=agent,
                action=random.choice(["scan_complete", "analysis_done", "alert_generated", "task_executed", "report_filed"]),
                result=f"{agent} completed operation. {random.randint(1,50)} indicators processed. {random.randint(0,5)} anomalies flagged.",
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 720)),
            )
            db.add(log)
        count += 60

        db.commit()
        print_header(f"SEED COMPLETE: {count}+ entities loaded")
        logger.info(f"Missions: {len(mission_objs)}")
        logger.info(f"Spatial Events: 120")
        logger.info(f"Intel Reports: 100")
        logger.info(f"Canary Entries: 150")
        logger.info(f"Agent Actions: 80")
        logger.info(f"Agent Logs: 60")
        print_header("="*60)

    except Exception as e:
        db.rollback()
        logger.error(f"SEED FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # If run directly, configure basic logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    seed_database()

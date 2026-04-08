# AEGIS Command Examples — Intermediate to Advanced

> Real-world workflow examples demonstrating multi-agent coordination, MCP tool integration, and database operations.

---

## 🟢 LEVEL 1: Intermediate — Basic Mission Execution

### 1.1 Corporate Security Audit
```bash
curl -X POST http://localhost:8000/api/missions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Plan Q3 cybersecurity audit for executive offsite. Monitor for insider threats, schedule emergency board syncs, and deploy canary tokens to detect unauthorized document access.",
    "mission_name": "OP Q3_AUDIT"
  }'
```
**What happens:** 6 agents coordinate → SENTINEL scans calendars, FORGE creates audit tasks, NEMESIS simulates attack vectors, ECHO deploys 3 canary tokens across channels.

### 1.2 Supply Chain Monitoring
```bash
curl -X POST http://localhost:8000/api/missions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Monitor semiconductor supply chain through South China Sea. Track vessel movements, port congestion at Shanghai and Singapore, and identify alternative routing options for critical components."
  }'
```
**What happens:** 240+ geospatial nodes monitored, supply disruption risks calculated, alternative ports identified, contingency shipping contracts pre-positioned.

### 1.3 Event Planning with Threat Detection
```bash
curl -X POST http://localhost:8000/api/missions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Organize M&A defense strategy meeting for Q2. Identify competitor intelligence gathering patterns, secure communication channels, and establish canary-protected document sharing."
  }'
```
**What happens:** NEMESIS simulates how competitors could intercept plans, BASTION builds secure communication playbook, COMMANDER produces 3 execution paths.

---

## 🟡 LEVEL 2: Advanced — Multi-Step Workflows

### 2.1 Insider Threat Investigation
```bash
curl -X POST http://localhost:8000/api/missions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Investigate suspected data exfiltration by employee with access to Project Atlas documents. Scan their calendar for meetings with external parties, check shared document access logs, deploy canary tokens in classified files, and create containment plan if threat score exceeds 0.65.",
    "mission_name": "OP INSIDER_HUNT"
  }'
```
**Full workflow:**
1. SENTINEL scans 72-hour calendar window + shared notes
2. FORGE creates investigation tasks for security team
3. NEMESIS calculates exfiltration probability (e.g., 0.72)
4. BASTION deploys access revocation playbook
5. ECHO injects canary tokens into 3 document channels
6. COMMANDER issues operational order with Overt/Covert/Contingency plans

**Verify results:**
```bash
# Check mission details
curl http://localhost:8000/api/missions/$(MISSION_ID)

# View agent actions
curl http://localhost:8000/api/agents/actions/$(MISSION_ID)

# Check canary deployment status
curl http://localhost:8000/api/canary/$(MISSION_ID)
```

### 2.2 Geopolitical Supply Chain Disruption
```bash
curl -X POST http://localhost:8000/api/missions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Assess impact of typhoon approaching South China Sea on semiconductor supply chain. Port of Shanghai may close for 5-7 days. Identify alternative routing through Kaohsiung and Busan. Pre-position inventory at EU and US warehouses. Calculate disruption probability and activate contingency contracts if risk exceeds threshold.",
    "mission_name": "OP TYHOON_SHIELD"
  }'
```
**Full workflow:**
- Spatial grid tracks 15 ports, 8 shipping lanes, 12 warehouse nodes
- NEMESIS simulates port closure cascading through 3 tiers of suppliers
- FORGE creates rerouting tasks and inventory transfer orders
- BASTION activates backup supplier contracts automatically
- Dashboard shows real-time risk propagation map

### 2.3 Cyber Incident Response
```bash
curl -X POST http://localhost:8000/api/missions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Respond to detected ransomware activity on corporate network. Identify affected systems, isolate compromised endpoints, deploy forensic investigation tasks, establish backup communication channels, and activate incident response playbook. Monitor lateral movement indicators and calculate time-to-contain estimate.",
    "mission_name": "OP RANSOMWARE_RESPONSE"
  }'
```
**Full workflow:**
- SENTINEL scans network logs, calendar (who's on-call), notes (previous IR playbooks)
- NEMESIS simulates ransomware lateral movement paths
- BASTION builds containment strategy with 4 countermeasures
- COMMANDER issues: Overt (isolate endpoints), Covert (forensic investigation), Contingency (full network shutdown)

---

## 🔴 LEVEL 3: Expert — Real-World Enterprise Scenarios

### 3.1 Defense: Military Force Protection
```bash
curl -X POST http://localhost:8000/api/missions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Conduct force protection assessment for forward-deployed unit in Eastern Europe. Monitor adversary military exercise patterns, track equipment movements via SIGINT, identify potential ambush routes, coordinate with NATO allied units for mutual support, and establish rapid response contingency if threat indicators exceed 0.70 threshold.",
    "mission_name": "OP FORWARD_RESOLVE"
  }'
```
**Real-world integration points:**
- Calendar → Unit rotation schedules, NATO coordination meetings
- Tasks → Patrol assignments, equipment maintenance, intel collection orders
- Notes → Classified threat assessments, rules of engagement
- Spatial Grid → 50+ tracked military positions across theater

### 3.2 Corporate M&A Defense
```bash
curl -X POST http://localhost:8000/api/missions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Defend against hostile takeover attempt by Apex Corp. Monitor their public filings for acquisition signals, track their executive travel patterns for meeting intelligence, deploy canary tokens in shared data room documents, establish alternative financing contingency, and create public relations response plan for leak scenarios.",
    "mission_name": "OP IRON_SHIELD"
  }'
```
**Full workflow:**
- SENTINEL monitors SEC filings, executive calendars, press releases
- NEMESIS simulates Apex's acquisition strategy and timing
- FORGE creates defensive tasks: poison pill preparation, white knight outreach
- ECHO deploys canary tokens in virtual data room to detect unauthorized document access
- COMMANDER issues: Overt (public defense strategy), Covert (poison pill preparation), Contingency (white knight activation)

### 3.3 Critical Infrastructure Protection
```bash
curl -X POST http://localhost:8000/api/missions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Protect national power grid from state-sponsored cyber attack. Monitor SCADA system anomalies, track threat actor infrastructure, deploy honeypot canary tokens in network segments, coordinate with DHS CISA and NSA, establish manual override procedures for critical substations, and calculate cascading failure probability.",
    "mission_name": "OP GRID_SHIELD"
  }'
```

### 3.4 Healthcare Supply Chain Resilience
```bash
curl -X POST http://localhost:8000/api/missions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Ensure uninterrupted supply of critical medications through global logistics network. Monitor 15 manufacturing facilities, 8 distribution hubs, 200+ transportation routes. Identify single points of failure in API (Active Pharmaceutical Ingredient) supply chain. Pre-position 30-day emergency stock at regional warehouses. Activate alternative suppliers if primary route disruption probability exceeds 0.60.",
    "mission_name": "OP PHARMA_SHIELD"
  }'
```

---

## 🔵 API COMMAND REFERENCE

### Mission Management
```bash
# List all missions
curl http://localhost:8000/api/missions

# Get specific mission details
curl http://localhost:8000/api/missions/{mission_id}

# Complete a mission
curl -X POST http://localhost:8000/api/missions/{mission_id}/complete

# Abort a mission
curl -X POST "http://localhost:8000/api/missions/{mission_id}/abort?reason=Threat+neutralized"
```

### Intelligence & Monitoring
```bash
# Live intelligence feed
curl http://localhost:8000/api/intel/fetch

# Threat-filtered intelligence
curl http://localhost:8000/api/intel/threats

# Spatial grid (GeoJSON for mapping)
curl http://localhost:8000/api/dashboard/spatial-grid

# Temporal query (time range)
curl -X POST http://localhost:8000/api/temporal/query \
  -H "Content-Type: application/json" \
  -d '{"start_time": "2026-04-01T00:00:00", "end_time": "2026-04-07T23:59:59"}'
```

### Security Audit
```bash
# Global canary audit
curl http://localhost:8000/api/canary/audit

# Mission-specific canary status
curl http://localhost:8000/api/canary/{mission_id}

# Webhook execution (real external actions)
curl -X POST http://localhost:8000/api/webhook/execute \
  -H "Content-Type: application/json" \
  -d '{"name": "Alert Slack", "url": "https://hooks.slack.com/...", "payload": {"text": "Threat detected"}}'
```

### Digital Twin Simulation
```bash
# Add entity to digital twin
curl -X POST http://localhost:8000/api/twin/entities \
  -H "Content-Type: application/json" \
  -d '{"id": "port_shanghai", "entity_type": "asset", "name": "Port of Shanghai", "risk_score": 0.65}'

# Add relationship
curl -X POST http://localhost:8000/api/twin/relationships \
  -H "Content-Type: application/json" \
  -d '{"source_id": "apt_corvus", "target_id": "port_shanghai", "relationship": "targeting", "strength": 0.85}'

# Run what-if scenario
curl -X POST http://localhost:8000/api/twin/scenario \
  -H "Content-Type: application/json" \
  -d '{"name": "Port Closure Impact", "description": "What if Shanghai closes for 7 days?", "threat_entity_id": "apt_corvus", "threat_severity": 0.85, "time_horizon_hours": 168}'
```

---

## 🟣 DATABASE QUERIES (For Verification)

```sql
-- View all active missions
SELECT name, status, threat_score, stress_test_score, created_at 
FROM missions WHERE status = 'executing' ORDER BY threat_score DESC;

-- View agent actions for a specific mission
SELECT agent_name, action_type, title, severity, timestamp 
FROM agent_actions 
WHERE mission_id = 'YOUR_MISSION_ID' 
ORDER BY timestamp;

-- View canary deployment status
SELECT tool_type, payload_id, status, created_at 
FROM canaries 
WHERE mission_id = 'YOUR_MISSION_ID';

-- View adversarial debate rounds
SELECT round_number, threat_score, nemesis_analysis, bastion_response 
FROM debate_rounds 
WHERE mission_id = 'YOUR_MISSION_ID' 
ORDER BY round_number;

-- Spatial events by type
SELECT event_type, COUNT(*) as count, MAX(timestamp) as latest 
FROM spatial_events 
GROUP BY event_type 
ORDER BY count DESC;

-- Intel reports by source type
SELECT metadata_->>'source_type' as source, COUNT(*) as reports 
FROM intel_reports 
GROUP BY source;
```

---

## 🎯 HACKATHON DEMO SCRIPT (5 Minutes)

### Minute 1: Show the System Running
```bash
# Open terminal, run:
curl http://localhost:8000/ping
# → Shows "AEGIS ONLINE" - system is live
```

### Minute 2: Execute a Real-World Mission
```bash
# Run the pre-written demo:
venv\Scripts\python.exe demo_real_world_workflow.py
# → Shows 7-step workflow executing end-to-end
```

### Minute 3: Show the UI
Open http://localhost:8501 in browser
→ Point to: DEFCON status, interactive map with 240+ markers, active missions

### Minute 4: Show Agent Coordination
Open http://localhost:3000 → Agent Activity tab
→ Show 220+ actions from 6 agents, 9 debate rounds with NEMESIS↔BASTION exchanges

### Minute 5: Show API Architecture
Open http://localhost:8000/docs
→ Scroll through 25+ REST endpoints, show WebSocket endpoint for real-time streaming

---

## 📋 QUICK REFERENCE: What Each Agent Does

| Agent | Role | Example Action |
|---|---|---|
| **COMMANDER** | Primary orchestrator | Decomposes directive into 5 sub-agent tasks |
| **SENTINEL** | Intel gathering | Scans 3 MCP sources, identifies anomalies |
| **FORGE** | Logistics | Creates tasks, maps dependencies, assigns resources |
| **NEMESIS** | Red Team | Calculates disruption probability (0.0-1.0), finds attack vectors |
| **BASTION** | Blue Team | Builds defense playbooks, neutralizes red team predictions |
| **ECHO** | Comms/Canary | Deploys canary tokens, drafts stakeholder communications |

---

*All commands assume services are running on localhost. For production deployment, replace localhost with your server address.*

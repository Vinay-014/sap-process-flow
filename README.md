# AEGIS v2.0 | Autonomous Executive & Geospatial Intelligence System

> **Google Gen AI Academy Hackathon Submission**
> *Strategic Command Center with Multi-Agent Adversarial Workflow Orchestration*

## Demo Video

[![AEGIS v2.0 Demonstration](https://drive.google.com/file/d/1EqRYhB0T_Q1etZXtdOHzvvc5Hlp-1nyq/view?usp=drivesdk)

*Click the link above to view the complete system walkthrough, including agent orchestration, adversarial debate cycles, geospatial intelligence visualization, and real-time canary security auditing.*

---

##  Problem Statement

AEGIS is a strategic command center that manages high-stakes operations via a multi-agent hierarchy, utilizing Google Cloud (AlloyDB, Cloud Run) and MCP tool integration. AEGIS optimizes for **resilience and asymmetric advantage**, not convenience.

---

##  Architecture Overview

![AEGIS Architecture Diagram](./frontend/Gemini_Generated_Image.PNG)

---

##  Agent Hierarchy

| Agent | Role | Function |
|-------|------|----------|
| **COMMANDER** | Orchestrator | Decomposes strategic directives into missions, synthesizes all agent outputs |
| **SENTINEL** | Intel/Surveillance | Scans Calendar, Notes, Tasks for anomalies and threat vectors |
| **FORGE** | Logistics | Resource mapping, task creation, timeline optimization |
| **NEMESIS** | Red Team | Adversarial simulation, disruption probability calculation |
| **BASTION** | Blue Team | Defensive countermeasures, incident response playbooks |
| **ECHO** | Comms & Deception | Stakeholder communications, canary injection for security audit |

---

##  Key Innovations 

### 1. Adversarial Stress Test Score
Every plan receives a **NEMESIS → BASTION** debate score. Plans aren't just generated — they're stress-tested through cyclic adversarial refinement.

### 2. Canary-Based Security Audit
ECHO injects decoy data into MCP tools. BASTION monitors for unauthorized "leaks," proving the system protects against tool-level vulnerabilities.

### 3. Multi-Path Execution with Hot-Swap
Three simultaneous task trees: **Overt** (standard), **Covert** (encrypted local), **Contingency** (dormant). When NEMESIS predicts disruption > 70%, contingency **hot-swaps** into active execution.

### 4. Spatial-Temporal Intelligence
Tasks with location data appear on a **geospatial grid** (Leaflet map), not just lists. Timeline scrubbing enables temporal analysis of resource movements.

---

##  Quick Start

### Prerequisites
* Python 3.12+
* Node.js 20+
* Docker & Docker Compose (optional)
* Google API Key (Gemini)

### Option 1: Local Setup (Recommended for Hackathon Demo)

#### Step 1: Start PostgreSQL
```bash
docker-compose up -d postgres
```

#### Step 2: Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your-api-key-here"
# Or add to .env file

# Start the backend
python main.py
# Backend runs at http://localhost:8000
```

#### Step 3: Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:3000
```

### Option 2: Docker Compose (Full Stack)
```bash
# Set your Google API key
export GOOGLE_API_KEY="your-api-key-here"

# Build and start everything
docker-compose up --build

# Access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

##  API Endpoints

### Missions
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/missions/execute` | Execute a new mission through full AEGIS pipeline |
| `GET` | `/api/missions` | List all missions |
| `GET` | `/api/missions/{id}` | Get mission detail with plans, canaries, logs |
| `POST` | `/api/missions/{id}/complete` | Mark mission as completed |
| `POST` | `/api/missions/{id}/abort` | Abort a running mission |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dashboard/cop` | Common Operating Picture |
| `GET` | `/api/dashboard/defcon` | DEFCON status with breakdown |

### Agents
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/agents/logs` | Agent execution logs |
| `GET` | `/api/agents/debate/{id}` | NEMESIS ↔ BASTION debate history |
| `GET` | `/api/agents/status` | Agent heartbeat status |

### Canary Security
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/canary/{id}` | Canary status for a mission |
| `GET` | `/api/canary/audit` | Global canary audit log |

### Spatial-Temporal
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/temporal/query` | Query events across time |
| `GET` | `/api/spatial/events` | Geospatial events for grid |
| `POST` | `/api/spatial/events` | Create spatial event |
| `GET` | `/api/spatial/heatmap` | Spatial heatmap data |

### MCP Bridge
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/mcp/execute` | Execute tool with classification |
| `GET` | `/api/mcp/audit` | MCP bridge audit log |
| `POST` | `/api/mcp/contingency/activate/{id}` | Activate contingency plans |

---

##  Database Schema

| Table | Purpose |
|-------|---------|
| `missions` | Core mission records with 3 execution paths |
| `task_trees` | Overt/Covert/Contingency tree roots |
| `task_tree_nodes` | Individual task nodes within trees |
| `canaries` | Security audit canary entries |
| `intel_reports` | Intelligence with vector embeddings (pgvector) |
| `spatial_events` | Geospatial events (PostGIS) |
| `agent_logs` | Structured agent execution logs |
| `debate_rounds` | NEMESIS-BASTION adversarial debate records |

---

##  Tech Stack

### Backend
* **FastAPI** — High-performance async API
* **LangGraph** — Cyclic multi-agent workflow orchestration
* **LangChain + Google Gemini** — LLM inference
* **SQLAlchemy + PostgreSQL** — Data persistence
* **pgvector** — Vector embeddings for semantic search
* **PostGIS** — Geospatial queries
* **MCP (Model Context Protocol)** — Tool integration

### Frontend
* **Next.js 14** — React framework
* **Tailwind CSS** — Utility-first styling
* **Framer Motion** — Smooth animations
* **Recharts** — Data visualization
* **Zustand** — State management
* **Leaflet** — Geospatial mapping
* **Lucide React** — Tactical iconography

---

## 📁 Project Structure

```
aegis-system/
├── main.py                      # FastAPI entry point
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Full stack orchestration
├── Dockerfile.backend           # Backend container
├── .env                         # Environment variables
│
├── src/
│   ├── agents/
│   │   ├── graph.py             # LangGraph orchestrator (6 agents)
│   │   ├── execution_engine.py  # Multi-path execution + hot-swap
│   │   ├── mcp_wrapper.py       # MCP tool integration
│   │   └── prompts_templates.py # Agent system prompts
│   │
│   ├── api/
│   │   └── router.py            # Complete REST API (25+ endpoints)
│   │
│   ├── db/
│   │   ├── models.py            # SQLAlchemy models (8 tables)
│   │   ├── engine.py            # DB engine + initialization
│   │   └── session.py           # Session management
│   │
│   └── mcp_servers/
│       ├── calendars.py         # Calendar MCP server
│       ├── tasks.py             # Task management MCP server
│       ├── notes.py             # Notes MCP server with canary
│       └── bridge.py            # Overt/Covert middleware
│
└── frontend/
    ├── package.json
    ├── next.config.js
    ├── tailwind.config.js
    └── src/
        ├── app/
        │   ├── layout.tsx
        │   ├── page.tsx
        │   └── globals.css
        ├── components/
        │   ├── WarRoom.tsx       # Main application shell
        │   ├── Header.tsx
        │   ├── Sidebar.tsx
        │   ├── COPDashboard.tsx
        │   ├── DefconDisplay.tsx
        │   ├── MissionPanel.tsx
        │   ├── AgentLogs.tsx
        │   ├── SpatialGrid.tsx
        │   ├── TemporalScrubber.tsx
        │   ├── CanaryMonitor.tsx
        │   └── DirectiveInput.tsx
        ├── lib/
        │   ├── api.ts            # API client
        │   └── store.ts          # Zustand state
        └── types/
            └── index.ts          # TypeScript types
```

---

##  Wrokflow

1. **Startinf the system** — `docker-compose up` or local setup
2. **Open http://localhost:3000** — See the War Room UI
3. **Enter a directive** in the bottom input: *"Plan executive offsite for Q2 review with security audit requirements"*
4. **Watch the COP Dashboard** — DEFCON level updates, agent heartbeat shows all 6 agents active
5. **Navigate to Missions** — See Overt/Covert/Contingency plans generated
6. **Check Agent Logs** — Watch the NEMESIS ↔ BASTION debate unfold
7. **Visit Canary Monitor** — See security canaries deployed and status
8. **Show Spatial Grid** — Tasks with locations appear on the map

---

##  Security

* Covert plans never leave the encrypted local storage
* Canary entries detect unauthorized MCP tool access
* MCP Bridge classifies all data flows (Overt vs Covert)
* Audit log tracks every tool execution

---

**Built with adversarial resilience. Optimized for asymmetric advantage.** 🛡️

import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
  // Increased to 5 minutes (300,000ms) to allow AI Agents to complete complex workflows
  timeout: 300000,
});

// API methods
export const aegisAPI = {
  // Health
  ping: () => api.get("/ping"),
  health: () => api.get("/api/health"),

  // Missions
  executeMission: (directive: string, name?: string) =>
    api.post("/api/missions/execute", { directive, mission_name: name }),
  listMissions: (status?: string, limit = 50) =>
    api.get("/api/missions", { params: { status, limit } }),
  getMission: (id: string) => api.get(`/api/missions/${id}`),
  completeMission: (id: string) => api.post(`/api/missions/${id}/complete`),
  abortMission: (id: string, reason: string) =>
    api.post(`/api/missions/${id}/abort`, null, { params: { reason } }),

  // Dashboard
  getCOP: () => api.get("/api/dashboard/cop"),
  getDEFCON: () => api.get("/api/dashboard/defcon"),

  // Agents
  getAgentLogs: (agent?: string, missionId?: string, limit = 100) =>
    api.get("/api/agents/logs", { params: { agent, mission_id: missionId, limit } }),
  getDebateHistory: (missionId: string) =>
    api.get(`/api/agents/debate/${missionId}`),
  getAgentStatus: () => api.get("/api/agents/status"),

  // Generic GET for flexible component usage
  get: (url: string) => api.get(url),

  // Canary
  getCanaryStatus: (missionId: string) =>
    api.get(`/api/canary/${missionId}`),
  getCanaryAudit: (status?: string, limit = 100) => {
    const params: Record<string, any> = { limit };
    if (status) params.status = status;
    return api.get("/api/canary/audit", { params });
  },

  // Temporal
  queryTemporal: (startTime?: string, endTime?: string, missionId?: string) =>
    api.post("/api/temporal/query", {
      start_time: startTime,
      end_time: endTime,
      mission_id: missionId,
    }),

  // Spatial
  getSpatialEvents: (missionId?: string, eventType?: string, limit = 200) =>
    api.get("/api/spatial/events", { params: { mission_id: missionId, event_type: eventType, limit } }),
  createSpatialEvent: (data: {
    description: string;
    event_type: string;
    latitude: number;
    longitude: number;
    mission_id?: string;
    metadata?: Record<string, any>;
  }) => api.post("/api/spatial/events", data),
  getSpatialHeatmap: (startTime?: string, endTime?: string) =>
    api.get("/api/spatial/heatmap", { params: { start_time: startTime, end_time: endTime } }),

  // MCP
  executeMCPTool: (
    toolName: string,
    args: Record<string, any>,
    classification = "overt",
    missionId?: string
  ) =>
    api.post("/api/mcp/execute", null, {
      params: { tool_name: toolName, args, classification, mission_id: missionId },
    }),
  getMCPAudit: (missionId?: string, classification?: string, limit = 100) =>
    api.get("/api/mcp/audit", { params: { mission_id: missionId, classification, limit } }),
  activateContingency: (missionId: string) =>
    api.post(`/api/mcp/contingency/activate/${missionId}`),
  
  // Database Seeding (for demo purposes)
  seedDatabase: () => api.post("/api/seed"),
};

export type {
  COPResponse,
  MissionResponse,
  AgentLogResponse,
  CanaryStatusResponse,
} from "@/types";

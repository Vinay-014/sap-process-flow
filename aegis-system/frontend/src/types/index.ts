export interface Mission {
  id: string;
  name: string;
  directive?: string;
  status: string;
  threat_score: number;
  stress_test_score: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface COPResponse {
  system_status: string;
  active_missions: number;
  total_threat_level: number;
  avg_stress_score: number;
  canary_security_posture: string;
  recent_missions: Mission[];
  agent_heartbeat: Record<string, { last_seen: string; status: string; recent_action: string }>;
}

export interface MissionResponse {
  mission_id: string;
  status: string;
  plan_summary: {
    overt: string;
    covert: string;
    contingency: string;
    hotswap_status: string;
  };
  threat_score: number;
  stress_test_score: number;
  executed_at: string;
}

export interface AgentLogResponse {
  logs: Array<{
    id: string;
    mission_id: string | null;
    agent: string;
    action: string;
    result: string;
    timestamp: string | null;
  }>;
  total: number;
}

export interface CanaryStatusResponse {
  mission_id: string;
  security_posture: string;
  canaries: Array<{
    id: string;
    mission_id: string;
    tool_type: string;
    payload_id: string;
    status: string;
    created_at: string | null;
    triggered_at: string | null;
  }>;
}

export interface DEFCONResponse {
  defcon: number;
  status: string;
  color: string;
  threat_score: number;
  active_missions: number;
  mission_breakdown: Array<{
    name: string;
    threat: number;
    stress: number;
  }>;
}

export interface SpatialEvent {
  id: string;
  description: string;
  event_type: string;
  timestamp: string | null;
  metadata: Record<string, any> | null;
  location?: { lat: number; lng: number };
}

export interface AgentStatus {
  [agent: string]: {
    status: string;
    last_action: string | null;
    last_seen: string | null;
    total_executions: number;
  };
}

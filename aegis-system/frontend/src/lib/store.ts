import { create } from "zustand";
import { aegisAPI } from "@/lib/api";
import type { COPResponse, DEFCONResponse, AgentStatus, Mission } from "@/types";

interface AEGISStore {
  // COP Data
  cop: COPResponse | null;
  defcon: DEFCONResponse | null;
  agentStatus: AgentStatus | null;

  // Missions
  missions: Mission[];
  selectedMission: Mission | null;
  missionDetail: any | null;

  // Logs
  agentLogs: any[];
  debateHistory: any[];

  // Spatial
  spatialEvents: any[];

  // UI State
  loading: boolean;
  error: string | null;
  directive: string;
  isExecuting: boolean;

  // Actions
  fetchCOP: () => Promise<void>;
  fetchDEFCON: () => Promise<void>;
  fetchAgentStatus: () => Promise<void>;
  fetchMissions: () => Promise<void>;
  fetchMissionDetail: (id: string) => Promise<void>;
  fetchAgentLogs: (missionId?: string) => Promise<void>;
  fetchDebateHistory: (missionId: string) => Promise<void>;
  fetchSpatialEvents: (missionId?: string) => Promise<void>;
  executeMission: (directive: string) => Promise<void>;
  setDirective: (d: string) => void;
  setSelectedMission: (m: Mission | null) => void;
}

export const useAEGISStore = create<AEGISStore>((set, get) => ({
  // Initial state
  cop: null,
  defcon: null,
  agentStatus: null,
  missions: [],
  selectedMission: null,
  missionDetail: null,
  agentLogs: [],
  debateHistory: [],
  spatialEvents: [],
  loading: false,
  error: null,
  directive: "",
  isExecuting: false,

  // Actions
  fetchCOP: async () => {
    try {
      const { data } = await aegisAPI.getCOP();
      set({ cop: data, error: null });
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  fetchDEFCON: async () => {
    try {
      const { data } = await aegisAPI.getDEFCON();
      set({ defcon: data, error: null });
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  fetchAgentStatus: async () => {
    try {
      const { data } = await aegisAPI.getAgentStatus();
      set({ agentStatus: data.agents, error: null });
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  fetchMissions: async () => {
    try {
      const { data } = await aegisAPI.listMissions();
      set({ missions: data.missions, error: null });
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  fetchMissionDetail: async (id: string) => {
    try {
      const { data } = await aegisAPI.getMission(id);
      set({ missionDetail: data, error: null });
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  fetchAgentLogs: async (missionId?: string) => {
    try {
      const { data } = await aegisAPI.getAgentLogs(undefined, missionId);
      set({ agentLogs: data.logs, error: null });
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  fetchDebateHistory: async (missionId: string) => {
    try {
      const { data } = await aegisAPI.getDebateHistory(missionId);
      set({ debateHistory: data.debates, error: null });
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  fetchSpatialEvents: async (missionId?: string) => {
    try {
      const { data } = await aegisAPI.getSpatialEvents(missionId);
      set({ spatialEvents: data.events, error: null });
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  executeMission: async (directive: string) => {
    set({ loading: true, isExecuting: true, error: null });
    try {
      const { data } = await aegisAPI.executeMission(directive);
      set({ isExecuting: false, loading: false, directive: "" });
      // Refresh data
      get().fetchCOP();
      get().fetchMissions();
    } catch (e: any) {
      set({ error: e.message, loading: false, isExecuting: false });
    }
  },

  setDirective: (d: string) => set({ directive: d }),
  setSelectedMission: (m: Mission | null) => set({ selectedMission: m }),
}));

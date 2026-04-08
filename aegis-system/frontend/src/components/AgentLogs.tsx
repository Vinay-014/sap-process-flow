"use client";

import { useEffect, useState } from "react";
import { useAEGISStore } from "@/lib/store";
import { Terminal, MessageSquare, Shield, Sword, Brain, Radio, Eye, Activity, AlertTriangle, AlertCircle, CheckCircle, ChevronDown, ChevronRight, Target, FileText, Lock, Key } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { aegisAPI } from "@/lib/api";

const agentIcons: Record<string, any> = {
  SENTINEL: Eye,
  FORGE: Target,
  NEMESIS: Sword,
  BASTION: Shield,
  ECHO: Radio,
  COMMANDER: Brain,
};

const agentColors: Record<string, string> = {
  SENTINEL: "text-blue-400",
  FORGE: "text-orange-400",
  NEMESIS: "text-red-400",
  BASTION: "text-green-400",
  ECHO: "text-purple-400",
  COMMANDER: "text-yellow-400",
};

const severityConfig: Record<string, { color: string; bg: string; icon: any }> = {
  critical: { color: "text-red-400", bg: "bg-red-400/10 border-red-400/30", icon: AlertTriangle },
  high: { color: "text-orange-400", bg: "bg-orange-400/10 border-orange-400/30", icon: AlertCircle },
  medium: { color: "text-yellow-400", bg: "bg-yellow-400/10 border-yellow-400/30", icon: AlertCircle },
  low: { color: "text-blue-400", bg: "bg-blue-400/10 border-blue-400/30", icon: AlertCircle },
  info: { color: "text-aegis-textMuted", bg: "bg-aegis-bg/50 border-aegis-border", icon: Activity },
};

export function AgentLogs() {
  const agentLogs = useAEGISStore((s) => s.agentLogs);
  const debateHistory = useAEGISStore((s) => s.debateHistory);
  const selectedMission = useAEGISStore((s) => s.selectedMission);
  const missions = useAEGISStore((s) => s.missions);
  const fetchAgentLogs = useAEGISStore((s) => s.fetchAgentLogs);
  const fetchDebateHistory = useAEGISStore((s) => s.fetchDebateHistory);
  const fetchMissions = useAEGISStore((s) => s.fetchMissions);
  const setSelectedMission = useAEGISStore((s) => s.setSelectedMission);

  const [activeSubTab, setActiveSubTab] = useState<"logs" | "actions" | "debate">("actions");
  const [actions, setActions] = useState<any[]>([]);
  const [allActions, setAllActions] = useState<any[]>([]);
  const [allDebates, setAllDebates] = useState<any[]>([]);
  const [expandedAction, setExpandedAction] = useState<string | null>(null);

  // Fetch missions on mount
  useEffect(() => {
    fetchMissions();
  }, [fetchMissions]);

  // Auto-select first mission if none selected
  useEffect(() => {
    if (!selectedMission && missions.length > 0) {
      setSelectedMission(missions[0]);
    }
  }, [selectedMission, missions, setSelectedMission]);

  const loadActions = async (missionId: string) => {
    try {
      const { data } = await aegisAPI.get(`/api/agents/actions/${missionId}`);
      setActions(data.actions || []);
    } catch (e) {
      console.error(e);
    }
  };

  const loadAllActions = async () => {
    try {
      const { data } = await aegisAPI.get("/api/agents/actions");
      setAllActions(data.actions || []);
    } catch (e) {
      console.error(e);
    }
  };

  const loadAllDebates = async () => {
    try {
      const { data } = await aegisAPI.get("/api/missions");
      const debates: any[] = [];
      for (const m of (data.missions || []).slice(0, 10)) {
        try {
          const resp = await aegisAPI.get(`/api/agents/debate/${m.id}`);
          if (resp.data.debates?.length > 0) {
            resp.data.debates.forEach((d: any) => {
              debates.push({ ...d, missionName: m.name });
            });
          }
        } catch {}
      }
      setAllDebates(debates);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (selectedMission) {
      fetchAgentLogs(selectedMission.id);
      fetchDebateHistory(selectedMission.id);
      loadActions(selectedMission.id);
    }
    loadAllActions();
    loadAllDebates();
  }, [selectedMission, fetchAgentLogs, fetchDebateHistory]);

  const displayActions = selectedMission ? actions : allActions;
  const displayDebates = selectedMission ? debateHistory : allDebates;

  return (
    <div className="h-full overflow-y-auto space-y-4">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Terminal className="w-5 h-5 text-aegis-primary" />
          <h2 className="text-lg font-bold font-mono">Agent Activity</h2>
        </div>
        <select
          value={selectedMission?.id || ""}
          onChange={(e) => {
            const m = missions.find((m: any) => m.id === e.target.value);
            if (m) setSelectedMission(m);
          }}
          className="bg-aegis-bg border border-aegis-border rounded-lg px-3 py-2 text-xs font-mono text-aegis-text focus:outline-none focus:border-aegis-primary"
        >
          <option value="">All Missions</option>
          {missions.map((m: any) => (
            <option key={m.id} value={m.id}>{m.name}</option>
          ))}
        </select>
      </div>

      {/* Sub-tabs */}
      <div className="flex gap-2">
        <button
          type="button"
          /*autoComplete="off"*/
          data-form-type="other"
          onClick={() => setActiveSubTab("actions")}
          className={`px-4 py-2 rounded-lg text-sm font-mono transition-all ${
            activeSubTab === "actions"
              ? "bg-aegis-primary/10 border border-aegis-primary/30 text-aegis-primary"
              : "border border-aegis-border text-aegis-textMuted hover:text-aegis-text"
          }`}
        >
          Actions ({displayActions.length})
        </button>
        <button
          type="button"
          data-form-type="other"
          onClick={() => setActiveSubTab("logs")}
          className={`px-4 py-2 rounded-lg text-sm font-mono transition-all ${
            activeSubTab === "logs"
              ? "bg-aegis-primary/10 border border-aegis-primary/30 text-aegis-primary"
              : "border border-aegis-border text-aegis-textMuted hover:text-aegis-text"
          }`}
        >
          Logs ({agentLogs.length})
        </button>
        <button
          type="button"
          data-form-type="other"
          onClick={() => setActiveSubTab("debate")}
          className={`px-4 py-2 rounded-lg text-sm font-mono transition-all ${
            activeSubTab === "debate"
              ? "bg-aegis-danger/10 border border-aegis-danger/30 text-aegis-danger"
              : "border border-aegis-border text-aegis-textMuted hover:text-aegis-text"
          }`}
        >
          Debate ({displayDebates.length})
        </button>
      </div>

      <AnimatePresence mode="wait">
        {activeSubTab === "actions" ? (
          <motion.div
            key="actions"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-3 max-h-[70vh] overflow-y-auto"
          >
            {displayActions.map((action) => {
              const Icon = agentIcons[action.agent] || Terminal;
              const color = agentColors[action.agent] || "text-aegis-textMuted";
              const sev = severityConfig[action.severity] || severityConfig.info;
              const SevIcon = sev.icon;
              const isExpanded = expandedAction === action.id;

              return (
                <div
                  key={action.id}
                  className={`rounded-lg border transition-all ${
                    isExpanded ? "bg-aegis-surface border-aegis-primary/30" : "bg-aegis-bg/30 border-aegis-border hover:border-aegis-primary/20"
                  }`}
                >
                  <button
                    type="button"
                    data-form-type="other"
                    onClick={() => setExpandedAction(isExpanded ? null : action.id)}
                    className="w-full p-4 flex items-start gap-3 text-left"
                  >
                    <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${color}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs font-mono font-bold ${color}`}>{action.agent}</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-aegis-primary/10 text-aegis-primary">
                          {action.action_type}
                        </span>
                        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${sev.color} ${sev.bg}`}>
                          <SevIcon className="w-3 h-3 inline mr-1" />
                          {action.severity}
                        </span>
                        <span className="text-[10px] font-mono text-aegis-textDim ml-auto">
                          {action.timestamp ? new Date(action.timestamp).toLocaleTimeString() : "-"}
                        </span>
                      </div>
                      <p className="text-sm font-mono text-aegis-text truncate">{action.title}</p>
                    </div>
                    {isExpanded ? <ChevronDown className="w-4 h-4 text-aegis-textDim" /> : <ChevronRight className="w-4 h-4 text-aegis-textDim" />}
                  </button>

                  {isExpanded && (
                    <div className="px-4 pb-4 pt-0 border-t border-aegis-border/50">
                      <div className="mt-3 space-y-3">
                        {/* Description */}
                        <div className="p-3 rounded-lg bg-aegis-bg/50">
                          <p className="text-[10px] font-mono text-aegis-textDim uppercase mb-1">DESCRIPTION</p>
                          <p className="text-xs font-mono text-aegis-textMuted whitespace-pre-wrap">{action.description}</p>
                        </div>

                        {/* Details */}
                        {action.details && (
                          <div className="p-3 rounded-lg bg-aegis-bg/50">
                            <p className="text-[10px] font-mono text-aegis-textDim uppercase mb-1">DETAILS</p>
                            <pre className="text-xs font-mono text-aegis-textMuted whitespace-pre-wrap max-h-40 overflow-y-auto">
                              {JSON.stringify(action.details, null, 2)}
                            </pre>
                          </div>
                        )}

                        {/* Evidence */}
                        {action.evidence && Object.keys(action.evidence).length > 0 && (
                          <div className="p-3 rounded-lg bg-aegis-primary/5 border border-aegis-primary/20">
                            <p className="text-[10px] font-mono text-aegis-primary uppercase mb-1 flex items-center gap-1">
                              <Key className="w-3 h-3" /> EVIDENCE
                            </p>
                            <pre className="text-xs font-mono text-aegis-textMuted whitespace-pre-wrap">
                              {JSON.stringify(action.evidence, null, 2)}
                            </pre>
                          </div>
                        )}

                        {/* Status */}
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                            action.status === "completed"
                              ? "bg-aegis-success/10 text-aegis-success"
                              : action.status === "failed"
                              ? "bg-aegis-danger/10 text-aegis-danger"
                              : "bg-aegis-warning/10 text-aegis-warning"
                          }`}>
                            {action.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
            {displayActions.length === 0 && (
              <p className="text-xs font-mono text-aegis-textDim text-center py-8">No actions recorded. Execute a mission first.</p>
            )}
          </motion.div>
        ) : activeSubTab === "logs" ? (
          <motion.div
            key="logs"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="glass rounded-xl p-4"
          >
            <div className="space-y-2 max-h-[60vh] overflow-y-auto">
              {agentLogs.map((log, i) => {
                const Icon = agentIcons[log.agent] || Terminal;
                const color = agentColors[log.agent] || "text-aegis-textMuted";

                return (
                  <div
                    key={log.id || i}
                    className="flex items-start gap-3 p-3 rounded-lg bg-aegis-bg/50 hover:bg-aegis-surfaceHover transition-colors"
                  >
                    <Icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${color}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-mono font-bold ${color}`}>{log.agent}</span>
                        <span className="text-[10px] font-mono text-aegis-textDim">{log.action}</span>
                        <span className="text-[10px] font-mono text-aegis-textDim ml-auto">
                          {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : "-"}
                        </span>
                      </div>
                      <p className="text-xs font-mono text-aegis-textMuted mt-1 truncate">{log.result}</p>
                    </div>
                  </div>
                );
              })}
              {agentLogs.length === 0 && (
                <p className="text-xs font-mono text-aegis-textDim text-center py-8">No agent logs available</p>
              )}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="debate"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-4"
          >
            {displayDebates.length > 0 ? (
              displayDebates.map((debate, i) => (
                <div key={debate.id || i} className="glass rounded-xl p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <MessageSquare className="w-4 h-4 text-aegis-textDim" />
                      <span className="text-sm font-mono font-bold text-aegis-text">Round {debate.round}</span>
                      {debate.missionName && (
                        <span className="text-[10px] font-mono text-aegis-textDim ml-2">— {debate.missionName}</span>
                      )}
                    </div>
                    <span className={`px-2 py-0.5 rounded text-xs font-mono ${
                      (debate.threat_score || 0) > 0.65
                        ? "bg-aegis-danger/10 text-aegis-danger"
                        : "bg-aegis-success/10 text-aegis-success"
                    }`}>
                      Threat: {(debate.threat_score || 0).toFixed(2)}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-3 rounded-lg bg-aegis-danger/5 border border-aegis-danger/20">
                      <div className="flex items-center gap-2 mb-2">
                        <Sword className="w-4 h-4 text-aegis-danger" />
                        <p className="text-xs font-mono font-bold text-aegis-danger">NEMESIS</p>
                      </div>
                      <p className="text-xs font-mono text-aegis-textMuted whitespace-pre-wrap line-clamp-6">
                        {debate.nemesis_analysis || "No analysis"}
                      </p>
                    </div>
                    <div className="p-3 rounded-lg bg-aegis-success/5 border border-aegis-success/20">
                      <div className="flex items-center gap-2 mb-2">
                        <Shield className="w-4 h-4 text-aegis-success" />
                        <p className="text-xs font-mono font-bold text-aegis-success">BASTION</p>
                      </div>
                      <p className="text-xs font-mono text-aegis-textMuted whitespace-pre-wrap line-clamp-6">
                        {debate.bastion_response || "No response"}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="glass rounded-xl p-8 text-center">
                <p className="text-xs font-mono text-aegis-textDim">No debate history available</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

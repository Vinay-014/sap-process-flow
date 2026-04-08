"use client";

import { useEffect } from "react";
import { useAEGISStore } from "@/lib/store";
import { Target, ChevronRight, AlertTriangle, Shield, Eye, Lock, AlertCircle } from "lucide-react";

export function MissionPanel() {
  const missions = useAEGISStore((s) => s.missions);
  const selectedMission = useAEGISStore((s) => s.selectedMission);
  const missionDetail = useAEGISStore((s) => s.missionDetail);
  const fetchMissions = useAEGISStore((s) => s.fetchMissions);
  const fetchMissionDetail = useAEGISStore((s) => s.fetchMissionDetail);
  const setSelectedMission = useAEGISStore((s) => s.setSelectedMission);

  useEffect(() => {
    fetchMissions();
  }, [fetchMissions]);

  const handleSelect = (mission: any) => {
    setSelectedMission(mission);
    fetchMissionDetail(mission.id);
  };

  return (
    <div className="h-full overflow-y-auto space-y-4">
      <div className="flex items-center gap-3 mb-6">
        <Target className="w-5 h-5 text-aegis-primary" />
        <h2 className="text-lg font-bold font-mono">Mission Management</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Mission List */}
        <div className="glass rounded-xl p-4">
          <h3 className="text-sm font-mono text-aegis-textDim uppercase mb-4">Operations</h3>
          <div className="space-y-2">
            {missions.map((m) => (
              <button
                key={m.id}
                onClick={() => handleSelect(m)}
                className={`w-full text-left p-3 rounded-lg border transition-all ${
                  selectedMission?.id === m.id
                    ? "border-aegis-primary bg-aegis-primary/10"
                    : "border-aegis-border hover:border-aegis-primary/50 hover:bg-aegis-surfaceHover"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <ChevronRight className="w-4 h-4 text-aegis-textDim" />
                    <div>
                      <p className="text-sm font-mono font-bold text-aegis-text">{m.name}</p>
                      <p className="text-[10px] font-mono text-aegis-textDim">
                        {m.created_at ? new Date(m.created_at).toLocaleString() : "-"}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-mono ${
                      m.status === "executing"
                        ? "bg-aegis-primary/10 text-aegis-primary"
                        : m.status === "completed"
                        ? "bg-aegis-success/10 text-aegis-success"
                        : "bg-aegis-textDim/10 text-aegis-textDim"
                    }`}
                  >
                    {m.status}
                  </span>
                </div>
              </button>
            ))}
            {missions.length === 0 && (
              <p className="text-xs font-mono text-aegis-textDim text-center py-8">No missions. Execute a directive below.</p>
            )}
          </div>
        </div>

        {/* Mission Detail */}
        <div className="glass rounded-xl p-4">
          <h3 className="text-sm font-mono text-aegis-textDim uppercase mb-4">Mission Detail</h3>
          {missionDetail ? (
            <div className="space-y-4">
              <div>
                <p className="text-xs font-mono text-aegis-textDim">DIRECTIVE</p>
                <p className="text-sm font-mono text-aegis-text mt-1">{missionDetail.directive || "N/A"}</p>
              </div>

              {/* Three Plans */}
              <div className="grid grid-cols-1 gap-3">
                {/* Overt */}
                <div className="p-3 rounded-lg bg-aegis-primary/5 border border-aegis-primary/20">
                  <div className="flex items-center gap-2 mb-2">
                    <Eye className="w-4 h-4 text-aegis-primary" />
                    <p className="text-xs font-mono font-bold text-aegis-primary">OVERT PLAN</p>
                  </div>
                  <p className="text-xs font-mono text-aegis-textMuted line-clamp-3">
                    {missionDetail.overt_plan || "No overt plan generated"}
                  </p>
                </div>

                {/* Covert */}
                <div className="p-3 rounded-lg glass-covert">
                  <div className="flex items-center gap-2 mb-2">
                    <Lock className="w-4 h-4 text-aegis-covert" />
                    <p className="text-xs font-mono font-bold text-aegis-covert">COVERT PLAN</p>
                  </div>
                  <p className="text-xs font-mono text-aegis-textMuted line-clamp-3">
                    {missionDetail.covert_plan ? missionDetail.covert_plan : "[ENCRYPTED - Local Storage Only]"}
                  </p>
                </div>

                {/* Contingency */}
                <div className="p-3 rounded-lg bg-aegis-warning/5 border border-aegis-warning/20">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="w-4 h-4 text-aegis-warning" />
                    <p className="text-xs font-mono font-bold text-aegis-warning">CONTINGENCY PLAN</p>
                  </div>
                  <p className="text-xs font-mono text-aegis-textMuted line-clamp-3">
                    {missionDetail.contingency_plan || "Standby — Activate if threat &gt; 70%"}
                  </p>
                </div>
              </div>

              {/* Scores */}
              <div className="flex gap-4">
                <div className="flex-1 p-3 rounded-lg bg-aegis-bg/50">
                  <p className="text-[10px] font-mono text-aegis-textDim">THREAT SCORE</p>
                  <p className={`text-xl font-bold font-mono ${
                    (missionDetail.threat_score || 0) > 0.65 ? "text-aegis-danger" : "text-aegis-success"
                  }`}>
                    {(missionDetail.threat_score || 0).toFixed(2)}
                  </p>
                </div>
                <div className="flex-1 p-3 rounded-lg bg-aegis-bg/50">
                  <p className="text-[10px] font-mono text-aegis-textDim">STRESS TEST</p>
                  <p className="text-xl font-bold font-mono text-aegis-primary">
                    {(missionDetail.stress_test_score || 0).toFixed(2)}
                  </p>
                </div>
              </div>

              {/* Canaries */}
              {missionDetail.canaries && missionDetail.canaries.length > 0 && (
                <div>
                  <p className="text-xs font-mono text-aegis-textDim flex items-center gap-2">
                    <Shield className="w-3 h-3" />
                    CANARY ENTRIES
                  </p>
                  <div className="flex gap-2 mt-2">
                    {missionDetail.canaries.map((c: any) => (
                      <span
                        key={c.id}
                        className={`px-2 py-1 rounded text-[10px] font-mono ${
                          c.status === "dormant"
                            ? "bg-aegis-success/10 text-aegis-success"
                            : "bg-aegis-danger/10 text-aegis-danger"
                        }`}
                      >
                        {c.tool_type}: {c.status}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs font-mono text-aegis-textDim text-center py-8">Select a mission to view details</p>
          )}
        </div>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useAEGISStore } from "@/lib/store";
import { ShieldAlert, Shield, AlertTriangle, CheckCircle, Eye, Activity } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { aegisAPI } from "@/lib/api";

export function CanaryMonitor() {
  const cop = useAEGISStore((s) => s.cop);
  const selectedMission = useAEGISStore((s) => s.selectedMission);

  const [canaryAudit, setCanaryAudit] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCanaryAudit();
  }, []);

  const fetchCanaryAudit = async () => {
    setLoading(true);
    try {
      const { data } = await aegisAPI.getCanaryAudit();
      setCanaryAudit(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const chartData = canaryAudit
    ? [
        { label: "Dormant", value: canaryAudit.summary?.dormant || 0, color: "#10b981" },
        { label: "Triggered", value: canaryAudit.summary?.triggered || 0, color: "#ef4444" },
        { label: "Neutralized", value: canaryAudit.summary?.neutralized || 0, color: "#3b82f6" },
      ]
    : [];

  return (
    <div className="h-full overflow-y-auto space-y-4">
      <div className="flex items-center gap-3 mb-6">
        <ShieldAlert className="w-5 h-5 text-aegis-canary" />
        <h2 className="text-lg font-bold font-mono">Canary Security Audit</h2>
      </div>

      {/* Security Posture Banner */}
      <div
        className={`p-4 rounded-xl border ${
          cop?.canary_security_posture === "SECURE"
            ? "bg-aegis-success/5 border-aegis-success/20"
            : "bg-aegis-danger/5 border-aegis-danger/20"
        }`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {cop?.canary_security_posture === "SECURE" ? (
              <CheckCircle className="w-6 h-6 text-aegis-success" />
            ) : (
              <AlertTriangle className="w-6 h-6 text-aegis-danger animate-pulse" />
            )}
            <div>
              <p className="text-sm font-mono font-bold text-aegis-text">Security Posture</p>
              <p
                className={`text-lg font-bold font-mono ${
                  cop?.canary_security_posture === "SECURE" ? "text-aegis-success" : "text-aegis-danger"
                }`}
              >
                {cop?.canary_security_posture || "UNKNOWN"}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs font-mono text-aegis-textDim">Total Canaries</p>
            <p className="text-2xl font-bold font-mono text-aegis-canary">
              {canaryAudit?.summary?.total || 0}
            </p>
          </div>
        </div>
      </div>

      {/* Chart + Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Chart */}
        <div className="glass rounded-xl p-4">
          <h3 className="text-sm font-mono text-aegis-textDim uppercase mb-4">Canary Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <XAxis dataKey="label" stroke="#475569" fontSize={10} />
              <YAxis stroke="#475569" fontSize={10} />
              <Tooltip
                contentStyle={{
                  background: "#12121a",
                  border: "1px solid #2a2a3a",
                  borderRadius: "8px",
                  fontSize: "12px",
                  color: "#e2e8f0",
                }}
                labelStyle={{ color: "#e2e8f0", fontWeight: "bold" }}
                itemStyle={{ color: "#e2e8f0" }}
              />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Canary List */}
        <div className="glass rounded-xl p-4 max-h-[280px] overflow-y-auto">
          <h3 className="text-sm font-mono text-aegis-textDim uppercase mb-4">Canary Entries</h3>
          <div className="space-y-2">
            {canaryAudit?.canaries?.slice(0, 10).map((canary: any) => (
              <div
                key={canary.id}
                className="flex items-center gap-3 p-2 rounded-lg bg-aegis-bg/50"
              >
                <Shield
                  className={`w-4 h-4 flex-shrink-0 ${
                    canary.status === "triggered"
                      ? "text-aegis-danger"
                      : canary.status === "neutralized"
                      ? "text-aegis-primary"
                      : "text-aegis-success"
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-mono text-aegis-text truncate">{canary.payload_id}</p>
                  <p className="text-[10px] font-mono text-aegis-textDim">{canary.tool_type}</p>
                </div>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                    canary.status === "dormant"
                      ? "bg-aegis-success/10 text-aegis-success"
                      : canary.status === "triggered"
                      ? "bg-aegis-danger/10 text-aegis-danger animate-pulse"
                      : "bg-aegis-primary/10 text-aegis-primary"
                  }`}
                >
                  {canary.status}
                </span>
              </div>
            ))}
            {(!canaryAudit?.canaries || canaryAudit.canaries.length === 0) && (
              <p className="text-xs font-mono text-aegis-textDim text-center py-4">No canary entries</p>
            )}
          </div>
        </div>
      </div>

      {/* Canary Workflow Explanation */}
      <div className="glass rounded-xl p-4">
        <h3 className="text-sm font-mono text-aegis-textDim uppercase mb-4">Canary Workflow</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { step: "1", icon: Shield, title: "Inject", desc: "ECHO deploys fake data into MCP tools" },
            { step: "2", icon: Eye, title: "Monitor", desc: "BASTION watches for unauthorized access" },
            { step: "3", icon: AlertTriangle, title: "Detect", desc: "Triggered canary signals potential leak" },
            { step: "4", icon: Activity, title: "Respond", desc: "Incident response playbook activated" },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.step} className="p-3 rounded-lg bg-aegis-bg/50 text-center">
                <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-aegis-canary/10 mb-2">
                  <Icon className="w-4 h-4 text-aegis-canary" />
                </div>
                <p className="text-xs font-mono font-bold text-aegis-text">
                  {item.step}. {item.title}
                </p>
                <p className="text-[10px] font-mono text-aegis-textDim mt-1">{item.desc}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

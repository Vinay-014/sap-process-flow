"use client";

import { useAEGISStore } from "@/lib/store";
import { DefconDisplay } from "@/components/DefconDisplay";
import { Shield, Target, Activity, AlertTriangle, CheckCircle, Clock } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

export function COPDashboard() {
  const cop = useAEGISStore((s) => s.cop);
  const defcon = useAEGISStore((s) => s.defcon);
  const agentStatus = useAEGISStore((s) => s.agentStatus);

  if (!cop) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-pulse text-aegis-textMuted font-mono">Loading COP...</div>
      </div>
    );
  }

  const statCards = [
    {
      label: "Active Missions",
      value: cop.active_missions,
      icon: Target,
      color: "text-aegis-primary",
      bgColor: "bg-aegis-primary/10",
    },
    {
      label: "Threat Level",
      value: cop.total_threat_level.toFixed(2),
      icon: AlertTriangle,
      color: "text-aegis-danger",
      bgColor: "bg-aegis-danger/10",
    },
    {
      label: "Avg Stress Score",
      value: (cop.avg_stress_score * 100).toFixed(1) + "%",
      icon: Activity,
      color: "text-aegis-warning",
      bgColor: "bg-aegis-warning/10",
    },
    {
      label: "Canary Posture",
      value: cop.canary_security_posture,
      icon: Shield,
      color: cop.canary_security_posture === "SECURE" ? "text-aegis-success" : "text-aegis-danger",
      bgColor: cop.canary_security_posture === "SECURE" ? "bg-aegis-success/10" : "bg-aegis-danger/10",
    },
  ];

  const chartData = cop.recent_missions
    .slice(0, 5)
    .map((m) => ({
      name: m.name,
      threat: m.threat_score,
      stress: m.stress_test_score,
    }))
    .reverse();

  return (
    <div className="h-full overflow-y-auto space-y-6">
      {/* Top Row: Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              className="glass rounded-xl p-4 scan-line"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-mono text-aegis-textDim uppercase">{stat.label}</p>
                  <p className={`text-2xl font-bold font-mono mt-1 ${stat.color}`}>{stat.value}</p>
                </div>
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`w-5 h-5 ${stat.color}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* DEFCON Display */}
      <DefconDisplay />

      {/* Middle Row: Chart + Agent Heartbeat */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Threat Chart */}
        <div className="lg:col-span-2 glass rounded-xl p-4">
          <h3 className="text-sm font-mono text-aegis-textDim uppercase mb-4">Mission Threat Analysis</h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData}>
                <XAxis dataKey="name" stroke="#475569" fontSize={10} />
                <YAxis stroke="#475569" fontSize={10} domain={[0, 1]} />
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
                <Bar dataKey="threat" name="Threat Score" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, i) => (
                    <Cell key={i} fill={entry.threat > 0.65 ? "#ef4444" : entry.threat > 0.3 ? "#f59e0b" : "#10b981"} />
                  ))}
                </Bar>
                <Bar dataKey="stress" name="Stress Score" radius={[4, 4, 0, 0]} fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[200px] flex items-center justify-center text-aegis-textDim font-mono text-sm">
              No mission data available
            </div>
          )}
        </div>

        {/* Agent Heartbeat */}
        <div className="glass rounded-xl p-4">
          <h3 className="text-sm font-mono text-aegis-textDim uppercase mb-4">Agent Heartbeat</h3>
          <div className="space-y-3">
            {Object.entries(cop.agent_heartbeat).map(([agent, data]) => (
              <div key={agent} className="flex items-center gap-3 p-2 rounded-lg bg-aegis-bg/50">
                <div
                  className={`w-2 h-2 rounded-full ${
                    data.status === "active" ? "bg-aegis-success animate-pulse" : "bg-aegis-textDim"
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-mono font-bold text-aegis-text">{agent}</p>
                  <p className="text-[10px] font-mono text-aegis-textDim truncate">{data.recent_action}</p>
                </div>
                <Clock className="w-3 h-3 text-aegis-textDim" />
              </div>
            ))}
            {Object.keys(cop.agent_heartbeat).length === 0 && (
              <p className="text-xs font-mono text-aegis-textDim text-center py-4">No agent activity</p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Missions */}
      <div className="glass rounded-xl p-4">
        <h3 className="text-sm font-mono text-aegis-textDim uppercase mb-4">Recent Missions</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm font-mono">
            <thead>
              <tr className="border-b border-aegis-border">
                <th className="text-left py-2 px-3 text-aegis-textDim">NAME</th>
                <th className="text-left py-2 px-3 text-aegis-textDim">STATUS</th>
                <th className="text-left py-2 px-3 text-aegis-textDim">THREAT</th>
                <th className="text-left py-2 px-3 text-aegis-textDim">STRESS</th>
                <th className="text-left py-2 px-3 text-aegis-textDim">CREATED</th>
              </tr>
            </thead>
            <tbody>
              {cop.recent_missions.map((m) => (
                <tr key={m.id} className="border-b border-aegis-border/50 hover:bg-aegis-surfaceHover transition-colors">
                  <td className="py-2 px-3 text-aegis-text">{m.name}</td>
                  <td className="py-2 px-3">
                    <span
                      className={`px-2 py-0.5 rounded text-xs ${
                        m.status === "executing"
                          ? "bg-aegis-primary/10 text-aegis-primary"
                          : m.status === "completed"
                          ? "bg-aegis-success/10 text-aegis-success"
                          : "bg-aegis-textDim/10 text-aegis-textDim"
                      }`}
                    >
                      {m.status}
                    </span>
                  </td>
                  <td className="py-2 px-3 font-bold text-aegis-text">{m.threat_score?.toFixed(2)}</td>
                  <td className="py-2 px-3 font-bold text-aegis-text">{m.stress_test_score?.toFixed(2)}</td>
                  <td className="py-2 px-3 text-aegis-textDim">{m.created_at ? new Date(m.created_at).toLocaleTimeString() : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {cop.recent_missions.length === 0 && (
            <p className="text-xs font-mono text-aegis-textDim text-center py-4">No missions recorded</p>
          )}
        </div>
      </div>
    </div>
  );
}

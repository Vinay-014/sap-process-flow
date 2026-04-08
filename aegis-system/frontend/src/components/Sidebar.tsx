"use client";

import { LayoutDashboard, Target, Terminal, Globe, Clock, ShieldAlert } from "lucide-react";

type TabType = "cop" | "missions" | "agents" | "spatial" | "temporal" | "canary";

interface SidebarProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

const navItems: { id: TabType; label: string; icon: any; description: string }[] = [
  { id: "cop", label: "Common Operating Picture", icon: LayoutDashboard, description: "Strategic dashboard" },
  { id: "missions", label: "Missions", icon: Target, description: "Mission management" },
  { id: "agents", label: "Agent Logic Logs", icon: Terminal, description: "NEMESIS vs BASTION debate" },
  { id: "spatial", label: "Spatial Grid", icon: Globe, description: "Geospatial intelligence" },
  { id: "temporal", label: "Temporal Scrubbing", icon: Clock, description: "Timeline analysis" },
  { id: "canary", label: "Canary Monitor", icon: ShieldAlert, description: "Security audit" },
];

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  return (
    <div className="h-full flex flex-col p-4">
      <div className="mb-6">
        <p className="text-xs font-mono text-aegis-textDim uppercase tracking-widest">Navigation</p>
      </div>

      <nav className="flex flex-col gap-1" role="navigation" aria-label="Main navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onTabChange(item.id)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all duration-200 ${
                isActive
                  ? "bg-aegis-primary/10 border border-aegis-primary/30 text-aegis-primary"
                  : "hover:bg-aegis-surfaceHover text-aegis-textMuted hover:text-aegis-text"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-aegis-primary" : ""}`} />
              <div>
                <p className={`text-sm font-medium ${isActive ? "text-aegis-primary" : ""}`}>{item.label}</p>
                <p className="text-[10px] text-aegis-textDim">{item.description}</p>
              </div>
            </button>
          );
        })}
      </nav>

      <div className="mt-auto pt-4 border-t border-aegis-border">
        <div className="px-3 py-2 rounded-md bg-aegis-bg/50">
          <p className="text-[10px] font-mono text-aegis-textDim uppercase">System</p>
          <p className="text-xs font-mono text-aegis-textMuted mt-1">AEGIS v2.0.0-HACKATHON</p>
          <p className="text-[10px] font-mono text-aegis-textDim">Google Gen AI Academy</p>
        </div>
      </div>
    </div>
  );
}

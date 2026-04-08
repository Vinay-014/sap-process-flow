"use client";

import { Shield, Radio, Activity } from "lucide-react";
import { useAEGISStore } from "@/lib/store";

export function Header() {
  const defcon = useAEGISStore((s) => s.defcon);
  const cop = useAEGISStore((s) => s.cop);

  const getDefconColor = (level: number) => {
    const colors: Record<number, string> = {
      1: "text-red-500 bg-red-500/10 border-red-500/30",
      2: "text-orange-500 bg-orange-500/10 border-orange-500/30",
      3: "text-yellow-500 bg-yellow-500/10 border-yellow-500/30",
      4: "text-blue-400 bg-blue-400/10 border-blue-400/30",
      5: "text-green-500 bg-green-500/10 border-green-500/30",
    };
    return colors[level] || colors[5];
  };

  return (
    <header className="h-14 border-b border-aegis-border bg-aegis-surface/80 backdrop-blur-sm flex items-center justify-between px-6 glass">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Shield className="w-6 h-6 text-aegis-primary" />
          <h1 className="text-lg font-bold tracking-wider font-mono">
            AEGIS<span className="text-aegis-textMuted text-sm ml-2">v2.0</span>
          </h1>
        </div>

        {defcon && (
          <div className={`px-3 py-1 rounded-md border text-sm font-mono font-bold ${getDefconColor(defcon.defcon)}`}>
            {defcon.status}
          </div>
        )}
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-sm text-aegis-textMuted">
          <Radio className="w-4 h-4 text-aegis-success animate-pulse" />
          <span>ADVERSARIAL_WORKFLOW_ACTIVE</span>
        </div>

        {cop && (
          <div className="flex items-center gap-4 text-sm font-mono">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-aegis-primary" />
              <span className="text-aegis-textMuted">MISSIONS:</span>
              <span className="text-aegis-text">{cop.active_missions}</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-aegis-canary" />
              <span className="text-aegis-textMuted">CANARY:</span>
              <span className={cop.canary_security_posture === "SECURE" ? "text-aegis-success" : "text-aegis-danger"}>
                {cop.canary_security_posture}
              </span>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

"use client";

import { useAEGISStore } from "@/lib/store";
import { Shield, AlertTriangle, Zap } from "lucide-react";
import { motion } from "framer-motion";

export function DefconDisplay() {
  const defcon = useAEGISStore((s) => s.defcon);

  if (!defcon) return null;

  const levels = [
    { level: 5, label: "NOMINAL", color: "#10b981", glow: "rgba(16, 185, 129, 0.3)" },
    { level: 4, label: "GUARDED", color: "#3b82f6", glow: "rgba(59, 130, 246, 0.3)" },
    { level: 3, label: "ELEVATED", color: "#f59e0b", glow: "rgba(245, 158, 11, 0.3)" },
    { level: 2, label: "HIGH", color: "#f97316", glow: "rgba(249, 115, 22, 0.3)" },
    { level: 1, label: "CRITICAL", color: "#ef4444", glow: "rgba(239, 68, 68, 0.5)" },
  ];

  const currentLevel = levels.find((l) => l.level === defcon.defcon) || levels[0];

  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-mono text-aegis-textDim uppercase flex items-center gap-2">
            <Shield className="w-4 h-4" />
            DEFCON Status
          </h3>
          <p className="text-xs font-mono text-aegis-textDim mt-1">
            Composite threat score: {defcon.threat_score.toFixed(2)}
          </p>
        </div>
        <motion.div
          className="flex items-center gap-4"
          animate={{ scale: defcon.defcon <= 2 ? [1, 1.05, 1] : 1 }}
          transition={{ repeat: defcon.defcon <= 2 ? Infinity : 0, duration: 1 }}
        >
          <div
            className="text-5xl font-bold font-mono"
            style={{ color: currentLevel.color, textShadow: `0 0 30px ${currentLevel.glow}` }}
          >
            {defcon.defcon}
          </div>
          <div>
            <p className="text-sm font-bold font-mono" style={{ color: currentLevel.color }}>
              {currentLevel.label}
            </p>
            <p className="text-[10px] font-mono text-aegis-textDim">{defcon.active_missions} active missions</p>
          </div>
        </motion.div>
      </div>

      {/* DEFCON Level Indicators */}
      <div className="flex gap-2 mt-4">
        {levels.map((l) => (
          <div
            key={l.level}
            className="flex-1 h-1.5 rounded-full transition-all duration-500"
            style={{
              backgroundColor: defcon.defcon <= l.level ? l.color : "#2a2a3a",
              boxShadow: defcon.defcon === l.level ? `0 0 10px ${l.glow}` : "none",
            }}
          />
        ))}
      </div>

      {defcon.defcon <= 2 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 flex items-center gap-2 p-3 rounded-lg bg-aegis-danger/10 border border-aegis-danger/30"
        >
          <AlertTriangle className="w-4 h-4 text-aegis-danger" />
          <p className="text-xs font-mono text-aegis-danger">
            ELEVATED THREAT POSTURE — Adversarial stress testing active
          </p>
          <Zap className="w-4 h-4 text-aegis-danger animate-pulse" />
        </motion.div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useAEGISStore } from "@/lib/store";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import { COPDashboard } from "@/components/COPDashboard";
import { MissionPanel } from "@/components/MissionPanel";
import { AgentLogs } from "@/components/AgentLogs";
import { DirectiveInput } from "@/components/DirectiveInput";
import { TemporalScrubber } from "@/components/TemporalScrubber";
import { SpatialGrid } from "@/components/SpatialGrid";
import { CanaryMonitor } from "@/components/CanaryMonitor";
import { DefconDisplay } from "@/components/DefconDisplay";
import { motion, AnimatePresence } from "framer-motion";

type TabType = "cop" | "missions" | "agents" | "spatial" | "temporal" | "canary";

export function WarRoom() {
  const [activeTab, setActiveTab] = useState<TabType>("cop");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const fetchCOP = useAEGISStore((s) => s.fetchCOP);
  const fetchDEFCON = useAEGISStore((s) => s.fetchDEFCON);
  const fetchAgentStatus = useAEGISStore((s) => s.fetchAgentStatus);
  const fetchMissions = useAEGISStore((s) => s.fetchMissions);

  // Initial data load
  useEffect(() => {
    fetchCOP();
    fetchDEFCON();
    fetchAgentStatus();
    fetchMissions();
  }, [fetchCOP, fetchDEFCON, fetchAgentStatus, fetchMissions]);

  // Auto-refresh every 10s
  useEffect(() => {
    const interval = setInterval(() => {
      fetchCOP();
      fetchDEFCON();
      fetchAgentStatus();
    }, 10000);
    return () => clearInterval(interval);
  }, [fetchCOP, fetchDEFCON, fetchAgentStatus]);

  const renderContent = () => {
    switch (activeTab) {
      case "cop":
        return <COPDashboard />;
      case "missions":
        return <MissionPanel />;
      case "agents":
        return <AgentLogs />;
      case "spatial":
        return <SpatialGrid />;
      case "temporal":
        return <TemporalScrubber />;
      case "canary":
        return <CanaryMonitor />;
      default:
        return <COPDashboard />;
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-aegis-bg text-aegis-text">
      <Header />

      <div className="flex flex-1 overflow-hidden">
        <AnimatePresence>
          {sidebarOpen && (
            <motion.aside
              initial={{ x: -280, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -280, opacity: 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="w-[280px] flex-shrink0 border-r border-aegis-border bg-aegis-surface"
            >
              <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
            </motion.aside>
          )}
        </AnimatePresence>

        <main className="flex-1 overflow-hidden relative">
          <button
            type="button"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="absolute top-4 left-4 z-50 p-2 rounded-lg bg-aegis-surface border border-aegis-border hover:border-aegis-primary transition-colors"
            aria-label="Toggle sidebar"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div className="h-full p-4 pt-16">
            {renderContent()}
          </div>
        </main>
      </div>

      <DirectiveInput />
    </div>
  );
}

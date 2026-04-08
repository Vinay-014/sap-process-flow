"use client";

import { useState, useCallback, useRef } from "react";
import { Clock, Play, Pause, SkipBack, SkipForward, Target, MapPin, Terminal, ChevronRight, Activity } from "lucide-react";
import { motion } from "framer-motion";
import { aegisAPI } from "@/lib/api";

const eventIcons: Record<string, { icon: typeof Target; color: string }> = {
  mission: { icon: Target, color: "text-aegis-primary" },
  agent_log: { icon: Terminal, color: "text-aegis-textMuted" },
  spatial_event: { icon: MapPin, color: "text-aegis-covert" },
};

const agentColors: Record<string, string> = {
  SENTINEL: "text-blue-400", FORGE: "text-orange-400", NEMESIS: "text-red-400",
  BASTION: "text-green-400", ECHO: "text-purple-400", COMMANDER: "text-yellow-400",
};

function EventDetail({ event }: { event: any }) {
  if (!event?.data) return null;
  const d = event.data;

  if (event.type === "mission") {
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2 mb-2">
          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
            d.status === "executing" ? "bg-aegis-primary/10 text-aegis-primary" :
            d.status === "completed" ? "bg-aegis-success/10 text-aegis-success" :
            "bg-aegis-textDim/10 text-aegis-textDim"
          }`}>
            {d.status?.toUpperCase()}
          </span>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-aegis-textDim font-mono">Mission Name</span>
            <span className="text-aegis-text font-mono font-bold">{d.name}</span>
          </div>
          {d.directive && (
            <div>
              <span className="text-[10px] font-mono text-aegis-textDim uppercase">Directive</span>
              <p className="text-xs font-mono text-aegis-textMuted mt-1 leading-relaxed">{d.directive}</p>
            </div>
          )}
          <div className="flex gap-4">
            <div className="flex-1 p-2 rounded bg-aegis-bg/50">
              <span className="text-[10px] font-mono text-aegis-textDim">Threat</span>
              <p className="text-sm font-mono font-bold text-aegis-danger">{d.threat_score?.toFixed(2)}</p>
            </div>
            <div className="flex-1 p-2 rounded bg-aegis-bg/50">
              <span className="text-[10px] font-mono text-aegis-textDim">Stress</span>
              <p className="text-sm font-mono font-bold text-aegis-primary">{d.stress_test_score?.toFixed(2)}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (event.type === "spatial_event") {
    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-aegis-covert/10 text-aegis-covert">
            {d.event_type?.replace(/_/g, " ").toUpperCase()}
          </span>
        </div>
        <p className="text-xs font-mono text-aegis-text leading-relaxed">{d.description}</p>
        <div className="flex gap-4">
          <div className="flex-1 p-2 rounded bg-aegis-bg/50">
            <span className="text-[10px] font-mono text-aegis-textDim">Zone</span>
            <p className="text-xs font-mono text-aegis-textMuted">{d.metadata?.zone || "N/A"}</p>
          </div>
          <div className="flex-1 p-2 rounded bg-aegis-bg/50">
            <span className="text-[10px] font-mono text-aegis-textDim">Risk</span>
            <p className="text-xs font-mono text-aegis-danger">{d.metadata?.risk_level || d.metadata?.priority || "N/A"}</p>
          </div>
        </div>
        {d.metadata?.latitude && (
          <div className="flex justify-between text-xs pt-2 border-t border-aegis-border">
            <span className="text-aegis-textDim font-mono">Coordinates</span>
            <span className="text-aegis-text font-mono">{d.metadata.latitude.toFixed(4)}, {d.metadata.longitude.toFixed(4)}</span>
          </div>
        )}
      </div>
    );
  }

  if (event.type === "agent_log") {
    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-[10px] font-mono font-bold ${agentColors[d.agent] || "text-aegis-textMuted"}`}>
            {d.agent}
          </span>
          <span className="text-[10px] font-mono text-aegis-textDim">→ {d.action}</span>
        </div>
        <p className="text-xs font-mono text-aegis-textMuted leading-relaxed">{d.result}</p>
      </div>
    );
  }

  return <pre className="text-[10px] font-mono text-aegis-textDim">{JSON.stringify(d, null, 2)}</pre>;
}

export function TemporalScrubber() {
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const handleQuery = async () => {
    setLoading(true);
    try {
      const { data } = await aegisAPI.queryTemporal(
        startTime || undefined,
        endTime || undefined
      );
      setTimeline(data.events || []);
      setCurrentIndex(0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const togglePlayback = () => {
    if (timeline.length === 0) return;
    if (!isPlaying) {
      setIsPlaying(true);
      intervalRef.current = setInterval(() => {
        setCurrentIndex((prev) => {
          if (prev >= timeline.length - 1) {
            setIsPlaying(false);
            if (intervalRef.current) clearInterval(intervalRef.current);
            return prev;
          }
          return prev + 1;
        });
      }, 2000);
    } else {
      setIsPlaying(false);
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
  };

  const currentEvent = timeline[currentIndex];

  return (
    <div className="h-full overflow-y-auto space-y-4">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Clock className="w-5 h-5 text-aegis-primary" />
          <h2 className="text-lg font-bold font-mono">Temporal Scrubbing</h2>
        </div>
        <span className="text-[10px] font-mono text-aegis-textDim">{timeline.length} events in range</span>
      </div>

      {/* Query Controls */}
      <div className="glass rounded-xl p-4">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <label className="text-[10px] font-mono text-aegis-textDim uppercase">Start Time</label>
            <input
              type="datetime-local"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="w-full bg-aegis-bg border border-aegis-border rounded-lg px-3 py-2 text-xs font-mono text-aegis-text focus:outline-none focus:border-aegis-primary"
            />
          </div>
          <div className="flex-1">
            <label className="text-[10px] font-mono text-aegis-textDim uppercase">End Time</label>
            <input
              type="datetime-local"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              className="w-full bg-aegis-bg border border-aegis-border rounded-lg px-3 py-2 text-xs font-mono text-aegis-text focus:outline-none focus:border-aegis-primary"
            />
          </div>
          <button
            type="button"
            onClick={handleQuery}
            disabled={loading}
            className="px-6 py-2 bg-aegis-primary hover:bg-aegis-primary/80 disabled:opacity-50 rounded-lg text-sm font-mono font-bold text-white transition-all self-end"
          >
            {loading ? "Querying..." : "Query"}
          </button>
        </div>
      </div>

      {/* Playback Controls */}
      {timeline.length > 0 && (
        <div className="glass rounded-xl p-4">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => { setCurrentIndex(0); setIsPlaying(false); }}
              className="p-2 rounded-lg bg-aegis-bg/50 hover:bg-aegis-surfaceHover transition-colors"
            >
              <SkipBack className="w-4 h-4 text-aegis-textMuted" />
            </button>
            <button
              type="button"
              onClick={togglePlayback}
              className="p-3 rounded-lg bg-aegis-primary/10 hover:bg-aegis-primary/20 transition-colors"
            >
              {isPlaying ? (
                <Pause className="w-5 h-5 text-aegis-primary" />
              ) : (
                <Play className="w-5 h-5 text-aegis-primary" />
              )}
            </button>
            <button
              type="button"
              onClick={() => { setCurrentIndex(timeline.length - 1); setIsPlaying(false); }}
              className="p-2 rounded-lg bg-aegis-bg/50 hover:bg-aegis-surfaceHover transition-colors"
            >
              <SkipForward className="w-4 h-4 text-aegis-textMuted" />
            </button>

            <div className="flex-1 ml-4">
              <div className="flex items-center justify-between text-xs font-mono text-aegis-textDim mb-1">
                <span>{currentIndex + 1} / {timeline.length}</span>
                <span>{currentEvent?.type?.replace("_", " ").toUpperCase()}</span>
              </div>
              <div className="h-2 bg-aegis-bg rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-aegis-primary"
                  animate={{ width: `${((currentIndex + 1) / timeline.length) * 100}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Current Event Detail */}
      {currentEvent && (
        <div className="glass rounded-xl p-4 border border-aegis-primary/30">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="w-4 h-4 text-aegis-primary" />
            <span className="text-sm font-mono font-bold text-aegis-text">EVENT #{currentIndex + 1}</span>
            <span className="text-[10px] font-mono text-aegis-textDim ml-auto">
              {currentEvent.timestamp ? new Date(currentEvent.timestamp).toLocaleString() : "-"}
            </span>
          </div>
          <EventDetail event={currentEvent} />
        </div>
      )}

      {/* Timeline List */}
      <div className="glass rounded-xl p-4 max-h-[40vh] overflow-y-auto">
        <h3 className="text-xs font-mono text-aegis-textDim uppercase mb-3">Timeline</h3>
        <div className="space-y-1">
          {timeline.map((event, i) => {
            const { icon: Icon, color } = eventIcons[event.type] || { icon: Activity, color: "text-aegis-textDim" };
            const isCurrent = i === currentIndex;
            return (
              <motion.button
                key={i}
                type="button"
                onClick={() => { setCurrentIndex(i); setIsPlaying(false); }}
                className={`w-full flex items-center gap-3 p-3 rounded-lg border text-left transition-all ${
                  isCurrent
                    ? "border-aegis-primary bg-aegis-primary/10"
                    : "border-aegis-border bg-aegis-bg/30 hover:border-aegis-primary/30"
                }`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.02 }}
              >
                <Icon className={`w-4 h-4 flex-shrink-0 ${color}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-mono text-aegis-text truncate">
                    {event.type === "mission" ? event.data?.name :
                     event.type === "spatial_event" ? event.data?.description :
                     event.type === "agent_log" ? `${event.data?.agent}: ${event.data?.action}` :
                     event.type}
                  </p>
                </div>
                <span className="text-[10px] font-mono text-aegis-textDim flex-shrink-0">
                  {event.timestamp ? new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "-"}
                </span>
                <ChevronRight className={`w-3 h-3 flex-shrink-0 ${isCurrent ? "text-aegis-primary" : "text-aegis-textDim"}`} />
              </motion.button>
            );
          })}
          {timeline.length === 0 && (
            <p className="text-xs font-mono text-aegis-textDim text-center py-8">
              Query a time range to view temporal events
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

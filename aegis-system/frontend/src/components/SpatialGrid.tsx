"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useAEGISStore } from "@/lib/store";
import { Globe, MapPin, Radio, AlertTriangle, Zap, Activity, CheckCircle, XCircle, Clock, Eye, Send, Shield, Target } from "lucide-react";
import dynamic from "next/dynamic";

const MapContainer = dynamic(() => import("react-leaflet").then((m) => m.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then((m) => m.TileLayer), { ssr: false });
const CircleMarker = dynamic(() => import("react-leaflet").then((m) => m.CircleMarker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then((m) => m.Popup), { ssr: false });

import "leaflet/dist/leaflet.css";
import { aegisAPI } from "@/lib/api";

const typeColors: Record<string, string> = {
  force_movement: "#3b82f6", patrol_route: "#60a5fa", surveillance: "#8b5cf6",
  anomaly: "#ef4444", exercise: "#f59e0b", port_congestion: "#f97316",
  vessel_tracking: "#06b6d4", supply_disruption: "#dc2626",
  risk_indicator: "#eab308", logistics_node: "#22c55e",
};

const severityOrder = ["critical", "high", "medium", "low", "info"];

function MetadataView({ metadata }: { metadata: Record<string, any> }) {
  const displayFields: Record<string, { label: string; icon?: string }> = {
    port: { label: "Port/Facility" },
    country: { label: "Country" },
    unit: { label: "Military Unit" },
    unit_type: { label: "Unit Type" },
    status: { label: "Status" },
    zone: { label: "Operational Zone" },
    priority: { label: "Priority" },
    risk_type: { label: "Risk Type" },
    risk_level: { label: "Risk Level" },
  };

  return (
    <div className="space-y-2">
      {Object.entries(metadata).map(([key, value]) => {
        if (key === "latitude" || key === "longitude") return null;
        const config = displayFields[key];
        if (!config) return null;
        return (
          <div key={key} className="flex items-center justify-between text-xs">
            <span className="text-aegis-textDim font-mono">{config.label}</span>
            <span className="text-aegis-text font-mono font-medium">{String(value)}</span>
          </div>
        );
      })}
      {metadata.latitude && metadata.longitude && (
        <div className="flex items-center justify-between text-xs pt-2 border-t border-aegis-border">
          <span className="text-aegis-textDim font-mono">Coordinates</span>
          <span className="text-aegis-text font-mono">
            {metadata.latitude.toFixed(4)}, {metadata.longitude.toFixed(4)}
          </span>
        </div>
      )}
    </div>
  );
}

function CommanderDecisionPanel({ event, onAction }: { event: any; onAction: (action: string) => void }) {
  const [comment, setComment] = useState("");
  const [selectedAction, setSelectedAction] = useState("");

  const recommendedActions: Record<string, string[]> = {
    port_congestion: ["Reroute vessels", "Activate alternate port", "Expedite customs clearance"],
    supply_disruption: ["Activate backup supplier", "Deploy reserve inventory", "Negotiate emergency logistics"],
    anomaly: ["Deploy reconnaissance", "Escalate to intelligence", "Increase monitoring frequency"],
    surveillance: ["Counter-surveillance measures", "Secure communications", "Deploy counter-intel"],
    risk_indicator: ["Risk assessment team deploy", "Stakeholder notification", "Mitigation plan activation"],
    force_movement: ["Update force posture", "Coordinate with allied units", "Adjust operational tempo"],
    vessel_tracking: ["Verify vessel identity", "Cross-reference manifest", "Flag for inspection"],
    patrol_route: ["Update patrol schedule", "Coordinate with maritime authority", "Adjust coverage area"],
    exercise: ["Deconflict with real operations", "Notify adjacent units", "Update exercise parameters"],
    logistics_node: ["Activate redundancy plan", "Secure supply line", "Pre-position resources"],
  };

  const actions = recommendedActions[event.event_type] || ["Assess situation", "Escalate to command", "Monitor and report"];

  return (
    <div className="mt-4 p-4 rounded-lg bg-aegis-bg/80 border border-aegis-primary/30">
      <div className="flex items-center gap-2 mb-3">
        <Shield className="w-4 h-4 text-aegis-primary" />
        <span className="text-sm font-mono font-bold text-aegis-primary">COMMANDER DECISION</span>
      </div>

      {/* Recommended Actions */}
      <div className="mb-3">
        <p className="text-[10px] font-mono text-aegis-textDim uppercase mb-2">Recommended Actions</p>
        <div className="space-y-1">
          {actions.map((action) => (
            <button
              key={action}
              type="button"
              onClick={() => setSelectedAction(action)}
              className={`w-full text-left px-3 py-2 rounded text-xs font-mono transition-all ${
                selectedAction === action
                  ? "bg-aegis-primary/20 border border-aegis-primary/50 text-aegis-primary"
                  : "bg-aegis-surface border border-aegis-border text-aegis-textMuted hover:border-aegis-primary/30"
              }`}
            >
              <Target className="w-3 h-3 inline mr-2" />
              {action}
            </button>
          ))}
        </div>
      </div>

      {/* Commander Comment */}
      <div className="mb-3">
        <p className="text-[10px] font-mono text-aegis-textDim uppercase mb-1">Commander Notes</p>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Add operational context or modify recommendation..."
          className="w-full bg-aegis-surface border border-aegis-border rounded px-3 py-2 text-xs font-mono text-aegis-text placeholder-aegis-textDim focus:outline-none focus:border-aegis-primary h-16 resize-none"
        />
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => selectedAction && onAction(`approve:${selectedAction}|${comment}`)}
          disabled={!selectedAction}
          className="flex-1 px-3 py-2 bg-aegis-success/20 border border-aegis-success/50 text-aegis-success rounded text-xs font-mono font-bold hover:bg-aegis-success/30 disabled:opacity-30 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-1"
        >
          <CheckCircle className="w-3 h-3" /> APPROVE
        </button>
        <button
          type="button"
          onClick={() => onAction(`reject|${comment}`)}
          className="flex-1 px-3 py-2 bg-aegis-danger/20 border border-aegis-danger/50 text-aegis-danger rounded text-xs font-mono font-bold hover:bg-aegis-danger/30 transition-all flex items-center justify-center gap-1"
        >
          <XCircle className="w-3 h-3" /> REJECT
        </button>
        <button
          type="button"
          onClick={() => onAction(`escalate|${comment}`)}
          className="flex-1 px-3 py-2 bg-aegis-warning/20 border border-aegis-warning/50 text-aegis-warning rounded text-xs font-mono font-bold hover:bg-aegis-warning/30 transition-all flex items-center justify-center gap-1"
        >
          <Clock className="w-3 h-3" /> ESCALATE
        </button>
      </div>
    </div>
  );
}

export function SpatialGrid() {
  const [spatialEvents, setSpatialEvents] = useState<any[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<any>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const [decisionLog, setDecisionLog] = useState<any[]>([]);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchEvents = useCallback(async () => {
    try {
      const { data } = await aegisAPI.getSpatialEvents(undefined, undefined, 500);
      setSpatialEvents(data.events || []);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (e) {
      console.error(e);
    }
  }, []);

  useEffect(() => {
    fetchEvents();
    intervalRef.current = setInterval(fetchEvents, 15000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [fetchEvents]);

  const handleCommanderAction = (action: string) => {
    const [type, ...rest] = action.split("|");
    const comment = rest.join("|");
    const entry = {
      id: Date.now(),
      event_id: selectedEvent?.id,
      event_type: selectedEvent?.event_type,
      event_desc: selectedEvent?.description,
      action: type,
      recommendation: type === "approve" ? comment.split(":")[1] || "N/A" : null,
      comment,
      timestamp: new Date().toLocaleTimeString(),
    };
    setDecisionLog((prev) => [entry, ...prev]);
    setSelectedEvent(null);
  };

  const eventCounts = spatialEvents.reduce((acc: Record<string, number>, e: any) => {
    acc[e.event_type] = (acc[e.event_type] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="h-full overflow-y-auto space-y-4">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Globe className="w-5 h-5 text-aegis-primary" />
          <h2 className="text-lg font-bold font-mono">Spatial Intelligence Grid</h2>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Activity className="w-3 h-3 text-aegis-success animate-pulse" />
            <span className="text-xs font-mono text-aegis-success">LIVE</span>
          </div>
          <span className="text-[10px] font-mono text-aegis-textDim">Updated: {lastUpdate}</span>
          <span className="text-[10px] font-mono text-aegis-textDim">| {spatialEvents.length} events</span>
        </div>
      </div>

      {/* Event Type Legend */}
      <div className="glass rounded-xl p-3">
        <div className="flex flex-wrap gap-3">
          {Object.entries(eventCounts).map(([type, count]) => (
            <div key={type} className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: typeColors[type] || "#64748b" }} />
              <span className="text-[10px] font-mono text-aegis-textMuted">{type.replace(/_/g, " ")}</span>
              <span className="text-[10px] font-mono text-aegis-text">{count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-[calc(100vh-360px)]">
        {/* Map */}
        <div className="lg:col-span-2 glass rounded-xl overflow-hidden relative">
          <div className="absolute inset-0">
            {typeof window !== "undefined" && spatialEvents.length > 0 && (
              <MapContainer
                center={[20, 0]}
                zoom={2}
                scrollWheelZoom={true}
                style={{ height: "100%", width: "100%" }}
                zoomControl={false}
              >
                <TileLayer
                  attribution="&copy; OpenStreetMap"
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />
                {spatialEvents.map((event: any, i: number) => {
                  const lat = event.metadata?.latitude;
                  const lng = event.metadata?.longitude;
                  if (!lat || !lng) return null;
                  return (
                    <CircleMarker
                      key={event.id || i}
                      center={[lat, lng]}
                      radius={event.metadata?.priority === "critical" ? 8 : 6}
                      fillColor={typeColors[event.event_type] || "#64748b"}
                      color={typeColors[event.event_type] || "#64748b"}
                      fillOpacity={0.8}
                      weight={2}
                      eventHandlers={{
                        click: () => setSelectedEvent(event),
                      }}
                    >
                      <Popup>
                        <div className="text-xs font-mono">
                          <p className="font-bold">{event.description}</p>
                          <p className="text-aegis-textMuted">{event.event_type.replace(/_/g, " ")}</p>
                          <p className="text-aegis-textDim">{new Date(event.timestamp).toLocaleString()}</p>
                        </div>
                      </Popup>
                    </CircleMarker>
                  );
                })}
              </MapContainer>
            )}
          </div>
        </div>

        {/* Right Panel: Event Details + Commander Decision */}
        <div className="flex flex-col gap-4 overflow-y-auto">
          {/* Selected Event Detail */}
          {selectedEvent ? (
            <div className="glass rounded-xl p-4 border border-aegis-primary/30">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-aegis-primary" />
                  <span className="text-sm font-mono font-bold text-aegis-text">EVENT DETAIL</span>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedEvent(null)}
                  className="text-aegis-textDim hover:text-aegis-text"
                >
                  <XCircle className="w-4 h-4" />
                </button>
              </div>

              {/* Event Description */}
              <div className="mb-3 p-3 rounded-lg bg-aegis-bg/50">
                <p className="text-xs font-mono text-aegis-text leading-relaxed">{selectedEvent.description}</p>
              </div>

              {/* Event Type Badge */}
              <div className="flex items-center gap-2 mb-3">
                <span
                  className="px-2 py-1 rounded text-[10px] font-mono font-bold"
                  style={{
                    backgroundColor: `${typeColors[selectedEvent.event_type] || "#64748b"}20`,
                    color: typeColors[selectedEvent.event_type] || "#64748b",
                    border: `1px solid ${typeColors[selectedEvent.event_type] || "#64748b"}40`,
                  }}
                >
                  {selectedEvent.event_type.replace(/_/g, " ").toUpperCase()}
                </span>
                {selectedEvent.metadata?.risk_level && (
                  <span className={`px-2 py-1 rounded text-[10px] font-mono font-bold ${
                    selectedEvent.metadata.risk_level === "critical" ? "bg-red-500/10 text-red-400 border border-red-500/30" :
                    selectedEvent.metadata.risk_level === "high" ? "bg-orange-500/10 text-orange-400 border border-orange-500/30" :
                    "bg-yellow-500/10 text-yellow-400 border border-yellow-500/30"
                  }`}>
                    {selectedEvent.metadata.risk_level.toUpperCase()} RISK
                  </span>
                )}
              </div>

              {/* Professional Metadata Display */}
              <MetadataView metadata={selectedEvent.metadata || {}} />

              {/* Commander Decision Panel */}
              <CommanderDecisionPanel event={selectedEvent} onAction={handleCommanderAction} />
            </div>
          ) : (
            <div className="glass rounded-xl p-4 flex items-center justify-center" style={{ minHeight: "200px" }}>
              <div className="text-center">
                <Eye className="w-8 h-8 text-aegis-textDim mx-auto mb-2" />
                <p className="text-xs font-mono text-aegis-textDim">Click any marker on the map to view details and take command decisions</p>
              </div>
            </div>
          )}

          {/* Commander Decision Log */}
          <div className="glass rounded-xl p-4 flex-1">
            <div className="flex items-center gap-2 mb-3">
              <Send className="w-3 h-3 text-aegis-primary" />
              <span className="text-xs font-mono font-bold text-aegis-textDim uppercase">Decision Log</span>
            </div>
            <div className="space-y-2 max-h-[300px] overflow-y-auto">
              {decisionLog.map((entry) => (
                <div key={entry.id} className="p-3 rounded-lg bg-aegis-bg/50 border border-aegis-border">
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                      entry.action === "approve" ? "bg-green-500/10 text-green-400" :
                      entry.action === "reject" ? "bg-red-500/10 text-red-400" :
                      "bg-yellow-500/10 text-yellow-400"
                    }`}>
                      {entry.action.toUpperCase()}
                    </span>
                    <span className="text-[10px] font-mono text-aegis-textDim">{entry.timestamp}</span>
                  </div>
                  <p className="text-[10px] font-mono text-aegis-textMuted line-clamp-2">{entry.event_desc}</p>
                  {entry.recommendation && entry.recommendation !== "N/A" && (
                    <p className="text-[10px] font-mono text-aegis-primary mt-1">→ {entry.recommendation}</p>
                  )}
                </div>
              ))}
              {decisionLog.length === 0 && (
                <p className="text-[10px] font-mono text-aegis-textDim text-center py-4">No decisions recorded yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

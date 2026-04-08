"use client";

import { useState } from "react";
import { useAEGISStore } from "@/lib/store";
import { Send, Loader2, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

export function DirectiveInput() {
  const [isExpanded, setIsExpanded] = useState(false);
  const directive = useAEGISStore((s) => s.directive);
  const isExecuting = useAEGISStore((s) => s.isExecuting);
  const error = useAEGISStore((s) => s.error);
  const setDirective = useAEGISStore((s) => s.setDirective);
  const executeMission = useAEGISStore((s) => s.executeMission);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !isExecuting && directive.trim()) {
      e.preventDefault();
      executeMission(directive);
    }
  };

  return (
    <motion.div
      className="border-t border-aegis-border bg-aegis-surface/90 backdrop-blur-sm"
      initial={false}
    >
      <div onKeyDown={handleKeyDown}>
        <div className="max-w-4xl mx-auto p-4">
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-aegis-primary flex-shrink-0" />
            <input
              type="text"
              value={directive}
              onChange={(e) => setDirective(e.target.value)}
              onFocus={() => setIsExpanded(true)}
              onBlur={() => !isExecuting && setIsExpanded(false)}
              placeholder="Enter strategic directive..."
              className="flex-1 bg-aegis-bg border border-aegis-border rounded-lg px-4 py-2.5 text-sm font-mono text-aegis-text placeholder-aegis-textDim focus:outline-none focus:border-aegis-primary focus:ring-1 focus:ring-aegis-primary/30 transition-all"
              disabled={isExecuting}
            />
            <button
              type="button"
              onClick={() => directive.trim() && !isExecuting && executeMission(directive)}
              disabled={isExecuting || !directive.trim()}
              className="px-6 py-2.5 bg-aegis-primary hover:bg-aegis-primary/80 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-mono font-bold text-white transition-all flex items-center gap-2"
            >
              {isExecuting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  EXECUTING
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  EXECUTE
                </>
              )}
            </button>
          </div>

          {error && (
            <motion.p
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-xs font-mono text-aegis-danger mt-2 ml-8"
            >
              ERROR: {error}
            </motion.p>
          )}
        </div>
      </div>
    </motion.div>
  );
}

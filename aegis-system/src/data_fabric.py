"""
AEGIS Real-Time Data Fabric
Continuous data ingestion from live sources: RSS feeds, news APIs, threat intel.
"""

import feedparser
import requests
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

logger = logging.getLogger("aegis.data_fabric")


@dataclass
class IntelItem:
    """Single intelligence item from any source."""
    source: str
    title: str
    summary: str
    url: str
    published: str
    severity: str  # info, low, medium, high, critical
    tags: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "title": self.title,
            "summary": self.summary[:500],
            "url": self.url,
            "published": self.published,
            "severity": self.severity,
            "tags": self.tags,
            "entities": self.entities,
            "timestamp": datetime.utcnow().isoformat(),
        }


class RSSFeedSource:
    """RSS/Atom feed intelligence source."""

    def __init__(self, name: str, url: str, severity: str = "medium", tags: List[str] = None):
        self.name = name
        self.url = url
        self.severity = severity
        self.tags = tags or []
        self.last_update: Optional[datetime] = None

    def fetch(self) -> List[IntelItem]:
        try:
            feed = feedparser.parse(self.url)
            items = []
            for entry in feed.entries[:20]:
                published = entry.get("published", entry.get("updated", ""))
                item = IntelItem(
                    source=self.name,
                    title=entry.get("title", "Untitled"),
                    summary=entry.get("summary", entry.get("description", "")),
                    url=entry.get("link", ""),
                    published=published,
                    severity=self.severity,
                    tags=self.tags,
                )
                items.append(item)
            self.last_update = datetime.utcnow()
            logger.info(f"RSS {self.name}: fetched {len(items)} items")
            return items
        except Exception as e:
            logger.error(f"RSS {self.name} fetch failed: {e}")
            return []


class ThreatIntelSource:
    """Open-source threat intelligence feeds."""

    def __init__(self):
        self.sources = [
            RSSFeedSource("US-CERT Alerts", "https://www.us-cert.gov/ncas/current-activity.xml", "high", ["cyber", "government"]),
            RSSFeedSource("Krebs on Security", "https://krebsonsecurity.com/feed/", "medium", ["security", "threats"]),
            RSSFeedSource("ThreatPost", "https://threatpost.com/feed/", "medium", ["threats", "vulnerabilities"]),
            RSSFeedSource("Dark Reading", "https://www.darkreading.com/rss.xml", "medium", ["enterprise", "security"]),
            RSSFeedSource("Reuters World", "https://feeds.reuters.com/reuters/worldNews", "low", ["geopolitical", "global"]),
            RSSFeedSource("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml", "low", ["geopolitical", "global"]),
        ]

    def fetch_all(self) -> List[IntelItem]:
        all_items = []
        for source in self.sources:
            items = source.fetch()
            all_items.extend(items)
        all_items.sort(key=lambda x: x.published or "", reverse=True)
        logger.info(f"Threat Intel: fetched {len(all_items)} total items from {len(self.sources)} sources")
        return all_items


class NewsAnalysisSource:
    """Analyze news for threat relevance using keyword matching."""

    THREAT_KEYWORDS = [
        "cyber attack", "data breach", "ransomware", "malware", "phishing",
        "insider threat", "espionage", "sabotage", "vulnerability", "exploit",
        "zero-day", "APT", "advanced persistent threat", "state-sponsored",
        "hostile takeover", "merger", "acquisition", "leak", "whistleblower",
    ]

    def filter_threats(self, items: List[IntelItem]) -> List[IntelItem]:
        """Filter items that match threat keywords."""
        threat_items = []
        for item in items:
            text = f"{item.title} {item.summary}".lower()
            if any(kw in text for kw in self.THREAT_KEYWORDS):
                item.severity = "high"
                item.tags.append("threat-related")
                threat_items.append(item)
        return threat_items


class RealTimeDataFabric:
    """
    Central data fabric that continuously ingests, analyzes, and distributes
    intelligence from multiple live sources.
    """

    def __init__(self):
        self.threat_intel = ThreatIntelSource()
        self.news_analyzer = NewsAnalysisSource()
        self.intel_cache: List[IntelItem] = []
        self.threat_cache: List[IntelItem] = []
        self.last_full_fetch: Optional[datetime] = None
        self.subscribers: List[Any] = []  # WebSocket connections

    async def fetch_intelligence(self) -> Dict[str, Any]:
        """Fetch all intelligence and return summary."""
        all_items = self.threat_intel.fetch_all()
        threat_items = self.news_analyzer.filter_threats(all_items)

        self.intel_cache = all_items[:100]
        self.threat_cache = threat_items[:50]
        self.last_full_fetch = datetime.utcnow()

        # Notify subscribers
        await self._notify_subscribers({
            "type": "intel_update",
            "total_items": len(all_items),
            "threat_items": len(threat_items),
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "total_intel": len(all_items),
            "threat_intel": len(threat_items),
            "sources_active": len(self.threat_intel.sources),
            "last_fetch": self.last_full_fetch.isoformat() if self.last_full_fetch else None,
            "top_threats": [t.to_dict() for t in threat_items[:10]],
            "recent_intel": [i.to_dict() for i in all_items[:20]],
        }

    def get_cached_intel(self, threat_only: bool = False) -> List[Dict[str, Any]]:
        """Return cached intelligence."""
        cache = self.threat_cache if threat_only else self.intel_cache
        return [item.to_dict() for item in cache]

    def subscribe(self, subscriber):
        """Add WebSocket subscriber for real-time updates."""
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        """Remove WebSocket subscriber."""
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)

    async def _notify_subscribers(self, message: Dict[str, Any]):
        """Broadcast message to all WebSocket subscribers."""
        for ws in self.subscribers[:]:
            try:
                await ws.send_json(message)
            except Exception:
                self.subscribers.remove(ws)


# Global instance
data_fabric = RealTimeDataFabric()

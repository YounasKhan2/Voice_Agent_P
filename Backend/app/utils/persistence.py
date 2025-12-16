from __future__ import annotations
import asyncio
import httpx
import time
from typing import Any, Dict, List
from ..config import get_settings

# Simple async fire-and-forget ingestion. In production you might batch or queue.

_last_ingest_time: float | None = None
_ingest_event_count: int = 0
_ingest_session_ids: set[str] = set()

async def ingest_events(session_meta: Dict[str, Any], events: List[Dict[str, Any]]) -> None:
    settings = get_settings()
    if not settings.django_base_url or not settings.ingest_token:
        return  # persistence not configured
    url = settings.django_base_url.rstrip('/') + '/api/ingest'
    payload = {"session": session_meta, "events": events}
    headers = {"X-INGEST-TOKEN": settings.ingest_token, "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                global _last_ingest_time, _ingest_event_count, _ingest_session_ids
                _last_ingest_time = time.time()
                _ingest_event_count += len(events)
                _ingest_session_ids.add(str(session_meta.get("id")))
    except Exception:
        # swallow errors to avoid impacting realtime path
        pass

def schedule_ingest(session_meta: Dict[str, Any], events: List[Dict[str, Any]]):
    try:
        asyncio.create_task( ingest_events(session_meta, events) )
    except RuntimeError:
        # if no loop (rare), ignore
        pass

def get_ingest_stats() -> Dict[str, Any]:
    return {
        "configured": bool(get_settings().django_base_url and get_settings().ingest_token),
        "last_ingest_ts": _last_ingest_time,
        "event_count": _ingest_event_count,
        "session_ids": list(_ingest_session_ids),
    }

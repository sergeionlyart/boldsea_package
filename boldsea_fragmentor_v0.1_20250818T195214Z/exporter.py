from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

@dataclass
class FragmentEnvelope:
    model_identifier: str
    document_ref: str
    text: str
    fragment_anchor: str
    category: Optional[List[str]]
    relations: Dict[str, Any]
    attributes: Dict[str, Any]
    confidence: float
    event_id: str
    actor: str
    created_at: str

def to_jsonl(envelopes: List[FragmentEnvelope]) -> str:
    import json
    return "\n".join(_to_event_payload(env) for env in envelopes)

def _to_event_payload(env: FragmentEnvelope) -> str:
    import json
    event = {
        "SetModel": f"Fragment: Model: {env.model_identifier}",
        "Document": env.document_ref,
        "Attributes": {
            "text": env.text,
            "fragment_anchor": env.fragment_anchor,
            "confidence": env.confidence,
        },
        "Relations": env.relations,
        "Extra": {
            "category": env.category or [],
            "attributes": env.attributes,
        },
        "EventMeta": {
            "event_id": env.event_id,
            "actor": env.actor,
            "created_at": env.created_at,
        },
    }
    return json.dumps(event, ensure_ascii=False)

def build_envelopes(predictions, document_ref: str, actor: str = "system") -> List[FragmentEnvelope]:
    now = datetime.utcnow().isoformat() + "Z"
    envs: List[FragmentEnvelope] = []
    for p in predictions:
        envs.append(FragmentEnvelope(
            model_identifier=p["schema"],
            document_ref=document_ref,
            text=p["text"],
            fragment_anchor=p["anchor"],
            category=p.get("category"),
            relations=p.get("relations", {}),
            attributes=p.get("attributes", {}),
            confidence=p.get("confidence", 0.0),
            event_id=str(uuid.uuid4()),
            actor=actor,
            created_at=now
        ))
    return envs

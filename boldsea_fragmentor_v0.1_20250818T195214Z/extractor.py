from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import re
from .schemas import SchemaType

@dataclass
class ExtractedFields:
    fields: Dict[str, Any]
    confidence: float

def _simple_term(s: str) -> str:
    s = s.strip(" .,:;«»\"'()[]{}\n\t")
    return re.sub(r"\s+", " ", s)

def extract_fields(schema: SchemaType, text: str) -> ExtractedFields:
    t = text.strip()

    if schema == SchemaType.DEFINITION:
        m = re.match(r"^([A-Za-zА-Яа-я0-9 _\-/]+?)\s*[—:-]\s*(.+)$", t)
        if m:
            term = _simple_term(m.group(1))
            includes = [w for w in re.findall(r"[A-Za-zА-Яа-я][A-Za-zА-Яа-я\- ]{2,}", m.group(2)) if len(w.split())<=4][:6]
            return ExtractedFields({"term": term, "includes": includes}, 0.7)
        m = re.search(r"^([A-Za-z][\w \-]{1,50})\s+is\s+a[n]?\s+([A-Za-z][\w \-]{1,80})", t, re.IGNORECASE)
        if m:
            term = _simple_term(m.group(1))
            inc = [_simple_term(m.group(2))]
            return ExtractedFields({"term": term, "includes": inc}, 0.6)
        return ExtractedFields({}, 0.3)

    if schema == SchemaType.COMPARISON:
        m = re.match(r"^([\wА-Яа-я \-]+?)\s+(?:vs|в отличие от)\s+([\wА-Яа-я \-]+)", t, re.IGNORECASE)
        if m:
            return ExtractedFields({"target": _simple_term(m.group(1)), "comparator": _simple_term(m.group(2))}, 0.6)
        return ExtractedFields({}, 0.3)

    if schema == SchemaType.CAUSAL_RELATION:
        m = re.search(r"(.+?)\s+приводит к\s+(.+)", t, re.IGNORECASE)
        if m:
            return ExtractedFields({"cause": [_simple_term(m.group(1))], "effect": [_simple_term(m.group(2))]}, 0.6)
        return ExtractedFields({}, 0.3)

    if schema == SchemaType.APPLICATION_CONTEXT:
        m = re.search(r"используется в\s+([A-Za-zА-Яа-я ,\-]+)", t, re.IGNORECASE)
        if m:
            dom = [d.strip() for d in re.split(r",| и ", m.group(1)) if d.strip()]
            return ExtractedFields({"domain": dom[:5]}, 0.6)
        return ExtractedFields({}, 0.3)

    if schema == SchemaType.EXAMPLE:
        m = re.search(r"например[:,]?\s+(.+)$", t, re.IGNORECASE)
        if m:
            return ExtractedFields({"illustrates": [_simple_term(m.group(1)[:120])]}, 0.5)
        return ExtractedFields({}, 0.3)

    if schema in (SchemaType.ARCHITECTURAL_COMPONENT, SchemaType.TECHNICAL_PROCESS, SchemaType.ALGORITHM,
                  SchemaType.CONCEPTUAL_MODEL, SchemaType.PRINCIPLE, SchemaType.PROBLEM_SOLUTION,
                  SchemaType.LIMITATIONS_AND_CHALLENGES, SchemaType.FUNCTIONALITY, SchemaType.CAPABILITIES,
                  SchemaType.SYSTEM_INTEGRATION, SchemaType.COMPONENT_INTERACTION, SchemaType.USE_CASE,
                  SchemaType.CONCEPT_IMPLEMENTATION, SchemaType.ENUMERATION, SchemaType.TABLE_ANALYSIS,
                  SchemaType.ADVANTAGE_DISADVANTAGE):
        return ExtractedFields({}, 0.3)

    if schema == SchemaType.CODE_SNIPPET:
        return ExtractedFields({}, 0.8)

    return ExtractedFields({}, 0.2)

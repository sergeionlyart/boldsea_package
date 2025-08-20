from __future__ import annotations
from typing import List, Dict, Any
from .reader import read_any
from .segmenter import segment_pages, FragmentCandidate
from .classifier import classify_fragment
from .extractor import extract_fields
from .schemas import SchemaType
from .exporter import build_envelopes, to_jsonl

def run_demo(path: str, max_pages: int = 3, max_frags: int = 60) -> Dict[str, Any]:
    pages = read_any(path)
    if max_pages and len(pages) > max_pages:
        pages = pages[:max_pages]
    cands: List[FragmentCandidate] = segment_pages(pages)
    results = []
    for c in cands[:max_frags]:
        cls = classify_fragment(c.text)
        ext = extract_fields(cls.schema, c.text)
        results.append({
            "page": c.page,
            "anchor": c.anchor,
            "text": c.text[:5000],
            "schema": cls.schema.value,
            "confidence": round((cls.confidence + ext.confidence) / 2, 3),
            "attributes": {},
            "relations": ext.fields,
        })
    return {
        "fragments": results,
        "pages_read": len(pages),
    }

def export_jsonl(results: Dict[str, Any], document_ref: str, out_path: str) -> str:
    envs = build_envelopes(results["fragments"], document_ref=document_ref)
    jsl = to_jsonl(envs)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(jsl)
    return out_path

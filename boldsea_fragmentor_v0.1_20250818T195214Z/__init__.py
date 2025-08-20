"""
boldsea_fragmentor
------------------
A lightweight pipeline that splits raw texts (articles/chapters) into
schema-typed fragments for later insertion into Boldsea as Fragment:* models.

Stages:
  1) ingest: read PDF/text to raw pages
  2) segment: make paragraph-like candidates with anchors
  3) classify: pick schema model via heuristics (LLM-ready interface)
  4) extract: schema-specific fields (heuristics now; pluggable LLM later)
  5) export: JSONL with attributes/relations per Boldsea ontology

This package does not call any external LLM by default. You can plug your client
by implementing the LLMExtractor interface in extractor.py.
"""
__all__ = ["schemas", "reader", "segmenter", "classifier", "extractor", "exporter"]

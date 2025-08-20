# boldsea_fragmentor

Pipeline to split raw text/PDF into Boldsea schema-typed fragments:
**Definition, Comparison, Causal Relation, Application Context, Example,
Architectural Component, Technical Process, Algorithm, Conceptual Model,
Principle, Problem Solution, Limitations And Challenges, Functionality,
Capabilities, System Integration, Component Interaction, Use Case,
Concept Implementation, Code Snippet, Enumeration, Table Analysis,
Advantage Disadvantage**.

Produces JSONL payloads ready to POST to your Boldsea API.

## Quickstart
```python
from boldsea_fragmentor.demo_run import run_demo, export_jsonl
res = run_demo("your.pdf", max_pages=3, max_frags=60)
export_jsonl(res, document_ref="Document:Individual:your_doc", out_path="fragments.jsonl")
```

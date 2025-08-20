from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List
import re
from .schemas import SchemaType

@dataclass
class Classified:
    schema: SchemaType
    confidence: float
    reasons: List[str]

RX = {
    "definition": re.compile(r"\bопределение\b|\bопределяется как\b|\bэто\b|\bis a\b|\brefers to\b", re.IGNORECASE),
    "comparison": re.compile(r"\bв отличие от\b|\bпо сравнению\b|\bсравнива(ет|ются)\b|\bvs\b|\bпротив\b", re.IGNORECASE),
    "cause": re.compile(r"\bприводит к\b|\bв результате\b|\bпотому что\b|\bобусловлен(о|а|ы)\b|\bdue to\b|\bresults? in\b", re.IGNORECASE),
    "application": re.compile(r"\bприменяется\b|\bиспользуется в\b|\bобласти применени|\bapplication context\b", re.IGNORECASE),
    "example": re.compile(r"\bнапример\b|\bпример(ом)?\b|\be\.g\.\b|\bfor example\b", re.IGNORECASE),
    "arch_component": re.compile(r"\bкомпонент\b|\bмодуль\b|\bдвижок\b|\bengine\b|\bконтроллер\b", re.IGNORECASE),
    "tech_process": re.compile(r"\bвходн(ые|ых)\b|\bвыходн(ые|ых)\b|\bpipeline\b|\bпроцесс\b", re.IGNORECASE),
    "algorithm": re.compile(r"\bалгоритм\b|\bметод\b|\bшаг(и)?\b|\bprocedure\b", re.IGNORECASE),
    "concept_model": re.compile(r"\bконцептуальн(ая|ой) модель\b|\bмодель\b.*\bконцепт\b", re.IGNORECASE),
    "principle": re.compile(r"\bпринцип\b|\bподход\b|\bконтрастирует\b|\bобеспечивает\b", re.IGNORECASE),
    "problem_solution": re.compile(r"\bпроблем(а|ы)\b|\bрешени(е|я)\b|\bподход\b", re.IGNORECASE),
    "limits": re.compile(r"\bограничени(е|я)\b|\bвызов(ы)?\b|\bсложност(ь|и)\b", re.IGNORECASE),
    "functionality": re.compile(r"\bфункциональност(ь|и)\b|\bфункци(я|и)\b", re.IGNORECASE),
    "capabilities": re.compile(r"\bвозможност(ь|и)\b|\bспособности\b", re.IGNORECASE),
    "integration": re.compile(r"\bинтеграци(я|и)\b|\bсовместимост(ь|и)\b|\bAPI\b", re.IGNORECASE),
    "component_interaction": re.compile(r"\bвзаимодействи(е|я)\b|\bобмен\b|\bчерез\b", re.IGNORECASE),
    "use_case": re.compile(r"\bсценари(й|я)\b|\bакто(р|ры)\b|\bпользователь\b|\bшаг(и)?\b", re.IGNORECASE),
    "concept_impl": re.compile(r"\bреализаци(я|и)\b|\bтехнологи(я|и)\b|\bфреймворк\b|\bframework\b", re.IGNORECASE),
    "enumeration": re.compile(r"(^|\n)[\-•\*] +|(^|\n)\d+[\)\.] +", re.IGNORECASE),
    "table": re.compile(r"\|.*\|.*\||\bтаблиц(а|ы)\b", re.IGNORECASE),
    "adv_disadv": re.compile(r"\bпреимущест(ва|во)\b|\bнедостатк(и|ов)\b|\bплюсы\b|\bминусы\b", re.IGNORECASE),
    "code": re.compile(r"```|\{{\}}|\bclass\b|\bdef\b|;\s*$|\bpublic\b|\bvoid\b|\bfunction\b", re.IGNORECASE),
}

def is_code_like(text: str) -> bool:
    if RX["code"].search(text):
        return True
    letters = sum(ch.isalpha() for ch in text)
    nonspace = sum(not ch.isspace() for ch in text)
    if nonspace > 0 and letters / nonspace < 0.5 and ("{" in text or ";" in text or "(" in text):
        return True
    return False

def classify_fragment(text: str) -> Classified:
    t = text.strip()
    reasons: List[str] = []

    if is_code_like(t):
        return Classified(schema=SchemaType.CODE_SNIPPET, confidence=0.95, reasons=["code-like"])

    if RX["enumeration"].search(t) and len(t) < 2000:
        reasons.append("bullet/numbered list")
        return Classified(schema=SchemaType.ENUMERATION, confidence=0.85, reasons=reasons)

    if RX["table"].search(t):
        reasons.append("table/matrix pattern")
        return Classified(schema=SchemaType.TABLE_ANALYSIS, confidence=0.8, reasons=reasons)

    if RX["adv_disadv"].search(t):
        reasons.append("pros/cons lexemes")
        return Classified(schema=SchemaType.ADVANTAGE_DISADVANTAGE, confidence=0.8, reasons=reasons)

    checks: List[tuple] = [
        (SchemaType.DEFINITION, "definition"),
        (SchemaType.COMPARISON, "comparison"),
        (SchemaType.CAUSAL_RELATION, "cause"),
        (SchemaType.APPLICATION_CONTEXT, "application"),
        (SchemaType.EXAMPLE, "example"),
        (SchemaType.ARCHITECTURAL_COMPONENT, "arch_component"),
        (SchemaType.TECHNICAL_PROCESS, "tech_process"),
        (SchemaType.ALGORITHM, "algorithm"),
        (SchemaType.CONCEPTUAL_MODEL, "concept_model"),
        (SchemaType.PRINCIPLE, "principle"),
        (SchemaType.PROBLEM_SOLUTION, "problem_solution"),
        (SchemaType.LIMITATIONS_AND_CHALLENGES, "limits"),
        (SchemaType.FUNCTIONALITY, "functionality"),
        (SchemaType.CAPABILITIES, "capabilities"),
        (SchemaType.SYSTEM_INTEGRATION, "integration"),
        (SchemaType.COMPONENT_INTERACTION, "component_interaction"),
        (SchemaType.USE_CASE, "use_case"),
        (SchemaType.CONCEPT_IMPLEMENTATION, "concept_impl"),
    ]

    top_schema = SchemaType.UNKNOWN
    top_hits = 0
    for schema, key in checks:
        if RX[key].search(t):
            reasons.append(key)
            top_schema = schema
            top_hits += 1

    if top_schema != SchemaType.UNKNOWN:
        conf = 0.6 + min(0.3, 0.1 * (top_hits - 1))
        return Classified(schema=top_schema, confidence=conf, reasons=reasons)

    if ":" in t and len(t) < 300:
        return Classified(schema=SchemaType.DEFINITION, confidence=0.5, reasons=["colon-short"])

    return Classified(schema=SchemaType.UNKNOWN, confidence=0.2, reasons=["fallback"])

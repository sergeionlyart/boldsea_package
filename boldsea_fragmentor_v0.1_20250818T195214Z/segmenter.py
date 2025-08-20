from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import re

@dataclass
class FragmentCandidate:
    page: int
    anchor: str
    text: str

def normalize_text(s: str) -> str:
    s = s.replace("\u00A0", " ").replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def split_into_paragraphs(page_num: int, page_text: str) -> List[FragmentCandidate]:
    txt = normalize_text(page_text)
    if not txt:
        return []
    chunks = re.split(r"\n\s*\n", txt)
    frags: List[FragmentCandidate] = []
    offset = 0
    for ch in chunks:
        ch = ch.strip()
        if not ch:
            offset += 1
            continue
        lines = [ln.strip() for ln in ch.split("\n")]
        if all(re.match(r"^([\-•\*]|\d+[\)\.]|[a-z]\))\s+", ln) or len(ln) < 160 for ln in lines) and len(lines) > 1:
            para = " ".join(lines)
        else:
            para = " ".join(lines)
        if len(para) < 10:
            offset += len(ch) + 2
            continue
        anchor = f"{page_num}:{offset}-{offset+len(ch)}"
        frags.append(FragmentCandidate(page=page_num, anchor=anchor, text=para))
        offset += len(ch) + 2
    return frags

def segment_pages(pages: List[Tuple[int, str]]) -> List[FragmentCandidate]:
    result: List[FragmentCandidate] = []
    for page_num, page_text in pages:
        result.extend(split_into_paragraphs(page_num, page_text))
    return result

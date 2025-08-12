"""Layout heuristics for OCR results."""
from __future__ import annotations
from typing import Dict, List, Tuple, Any
import numpy as np

Line = Dict[str, Any]


def _line_height(line: Line) -> float:
    bbox = line["bbox"]
    y = [p[1] for p in bbox]
    return float(max(y) - min(y))


def _line_width(line: Line) -> float:
    bbox = line["bbox"]
    x = [p[0] for p in bbox]
    return float(max(x) - min(x))


def classify_lines(lines: List[Line], page_size: Tuple[int, int], config: Dict[str, Any]) -> Tuple[List[Line], float]:
    """Classify lines as headings or paragraphs.

    Returns updated line dicts with ``level`` and the page's median line height.
    """
    if not lines:
        return [], 0.0
    heights = [_line_height(l) for l in lines]
    median_h = float(np.median(heights))
    width = float(page_size[0])
    out: List[Line] = []
    prev_bottom = 0.0
    for line, h in zip(lines, heights):
        bbox = line["bbox"]
        x = [p[0] for p in bbox]
        y = [p[1] for p in bbox]
        line_width = _line_width(line)
        center_x = (max(x) + min(x)) / 2.0
        gap = min(y) - prev_bottom
        prev_bottom = max(y)
        text = line.get("text", "")
        level = "p"
        if h > config["heading_threshold_h1"] * median_h:
            level = "h1"
        elif (
            h > config["heading_threshold_h2"] * median_h
            and line_width < 0.75 * width
            and (
                (config["heading_extra_rules"].get("centered") and abs(center_x - width / 2) < 0.05 * width)
                or (config["heading_extra_rules"].get("all_caps") and text.isupper())
                or (config["heading_extra_rules"].get("big_gap") and gap > 0.8 * median_h)
            )
        ):
            level = "h2"
        out_line = dict(line)
        out_line["level"] = level
        out_line["height"] = h
        out.append(out_line)
    return out, median_h


def build_blocks(lines: List[Line], median_h: float, page_size: Tuple[int, int], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Merge lines into text blocks (paragraphs and headings)."""
    width = float(page_size[0])
    blocks: List[Dict[str, Any]] = []
    para: List[Line] = []
    prev_bottom = None
    prev_left = None
    for line in lines:
        bbox = line["bbox"]
        x = [p[0] for p in bbox]
        y = [p[1] for p in bbox]
        left = min(x)
        top = min(y)
        if line["level"] != "p":
            if para:
                blocks.append({"type": "p", "text": _merge_para(para, config)})
                para = []
            blocks.append({"type": line["level"], "text": line["text"]})
            prev_bottom = max(y)
            prev_left = left
            continue
        if not para:
            para.append(line)
            prev_bottom = max(y)
            prev_left = left
            continue
        gap = top - (prev_bottom or 0)
        if (
            abs(left - (prev_left or 0)) <= config["indent_tolerance"] * width
            and gap <= config["paragraph_merge_gap"] * median_h
        ):
            para.append(line)
        else:
            blocks.append({"type": "p", "text": _merge_para(para, config)})
            para = [line]
        prev_bottom = max(y)
        prev_left = left
    if para:
        blocks.append({"type": "p", "text": _merge_para(para, config)})
    return blocks


def _merge_para(lines: List[Line], config: Dict[str, Any]) -> str:
    texts: List[str] = []
    for line in lines:
        t = line.get("text", "")
        if (
            texts
            and config.get("hyphen_merge")
            and texts[-1].endswith("-")
            and t[:1].islower()
        ):
            texts[-1] = texts[-1][:-1] + t
        else:
            texts.append(t)
    sep = "\n" if config.get("keep_line_breaks") else " "
    return sep.join(texts)


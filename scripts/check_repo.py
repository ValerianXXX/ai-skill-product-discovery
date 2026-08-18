#!/usr/bin/env python3
"""Run lightweight, dependency-free checks for this documentation repository."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "CONTRIBUTING.md",
    "methodology/product-discovery-framework.md",
    "methodology/evidence-model.md",
    "methodology/critical-data-gap-test.md",
    "methodology/scoring-model.md",
    "methodology/validation-ladder.md",
    "cases/billfit/README.md",
    "cases/billfit/discovery-timeline.md",
    "cases/billfit/opportunity-matrix.md",
    "cases/billfit/product-decisions.md",
    "cases/billfit/evidence-ledger.md",
    "cases/billfit/validation-status.md",
    "data/initial-opportunity-screen.csv",
    "data/critical-data-opportunity-screen.csv",
    "data/evidence-ledger.csv",
    "data/github-trend-summary.csv",
    "templates/case-study-template.md",
]

TEXT_SUFFIXES = {".md", ".csv", ".py", ".yml", ".yaml", ".cff"}
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
UNFINISHED_RE = re.compile(r"\b(" + "|".join(("TO" + "DO", "T" + "BD", "FIX" + "ME")) + r")\b")


def text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"LICENSE", ".gitignore"}:
            files.append(path)
    return sorted(files)


def check_required(errors: list[str]) -> None:
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")


def check_text(errors: list[str]) -> None:
    for path in text_files():
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if "\t" in text:
            errors.append(f"tab character: {relative}")
        for number, line in enumerate(text.splitlines(), start=1):
            if line.endswith((" ", "\t")):
                errors.append(f"trailing whitespace: {relative}:{number}")
            if CJK_RE.search(line):
                errors.append(f"non-English CJK character: {relative}:{number}")
        if not relative.startswith("templates/") and UNFINISHED_RE.search(text):
            errors.append(f"unfinished marker outside templates: {relative}")


def normalized_link_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if " " in target and not target.startswith(("http://", "https://")):
        target = target.split(" ", 1)[0]
    return unquote(target.split("#", 1)[0])


def check_markdown_links(errors: list[str]) -> None:
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(text):
            target = normalized_link_target(raw)
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"relative link escapes repository: {path.relative_to(ROOT)} -> {raw}")
                continue
            if not resolved.exists():
                errors.append(f"broken relative link: {path.relative_to(ROOT)} -> {raw}")


def read_csv(relative: str, errors: list[str]) -> list[dict[str, str]]:
    path = ROOT / relative
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or any(not name for name in reader.fieldnames):
                errors.append(f"invalid CSV header: {relative}")
                return []
            rows = list(reader)
    except (OSError, csv.Error) as exc:
        errors.append(f"cannot parse CSV {relative}: {exc}")
        return []
    if not rows:
        errors.append(f"CSV has no data rows: {relative}")
    return rows


def as_int(row: dict[str, str], field: str, relative: str, errors: list[str]) -> int:
    try:
        return int(row[field])
    except (KeyError, TypeError, ValueError):
        errors.append(f"invalid integer {field} in {relative}: {row.get(field)!r}")
        return 0


def check_initial_scores(errors: list[str]) -> None:
    relative = "data/initial-opportunity-screen.csv"
    rows = read_csv(relative, errors)
    weighted = {
        "reach_score": 20,
        "frequency_score": 15,
        "pain_score": 15,
        "whitespace_score": 15,
        "mvp_ease_score": 15,
        "ai_leverage_score": 10,
        "acquisition_score": 5,
        "monetization_score": 5,
    }
    for row in rows:
        scores = {field: as_int(row, field, relative, errors) for field in weighted}
        if any(value < 1 or value > 5 for value in scores.values()):
            errors.append(f"score outside 1-5 in {relative}: {row.get('candidate')}")
        expected_gross = sum(scores[field] * weight for field, weight in weighted.items()) // 5
        gross = as_int(row, "gross_score", relative, errors)
        risk = as_int(row, "risk_deduction", relative, errors)
        final = as_int(row, "final_score", relative, errors)
        if gross != expected_gross:
            errors.append(f"gross score mismatch for {row.get('candidate')}: {gross} != {expected_gross}")
        if final != gross - risk:
            errors.append(f"final score mismatch for {row.get('candidate')}: {final} != {gross - risk}")


def check_critical_data_scores(errors: list[str]) -> None:
    relative = "data/critical-data-opportunity-screen.csv"
    rows = read_csv(relative, errors)
    weighted = {
        "critical_data_necessity": 20,
        "authoritative_data_access": 15,
        "deterministic_uplift": 15,
        "user_input_availability": 10,
        "narrow_scope_feasibility": 10,
        "maintenance_feasibility": 10,
        "human_gate_clarity": 10,
        "in_ai_distribution_fit": 5,
        "economic_or_access_value": 5,
    }
    for row in rows:
        scores = {field: as_int(row, field, relative, errors) for field in weighted}
        if any(value < 1 or value > 5 for value in scores.values()):
            errors.append(f"score outside 1-5 in {relative}: {row.get('candidate_family')}")
        expected = sum(scores[field] * weight for field, weight in weighted.items()) // 5
        actual = as_int(row, "weighted_score", relative, errors)
        if actual != expected:
            errors.append(f"weighted score mismatch for {row.get('candidate_family')}: {actual} != {expected}")


def check_evidence(errors: list[str]) -> None:
    relative = "data/evidence-ledger.csv"
    rows = read_csv(relative, errors)
    ids = [row.get("id", "") for row in rows]
    if any(not evidence_id for evidence_id in ids):
        errors.append(f"blank evidence id in {relative}")
    duplicates = sorted({evidence_id for evidence_id in ids if ids.count(evidence_id) > 1})
    if duplicates:
        errors.append(f"duplicate evidence ids in {relative}: {', '.join(duplicates)}")
    allowed_strength = {"S1", "S2", "S3", "S4", "S5"}
    allowed_states = {"Observed", "Derived", "Inferred", "Assumed", "Tested", "Validated", "Rejected"}
    for row in rows:
        if row.get("source_strength") not in allowed_strength:
            errors.append(f"invalid source strength for {row.get('id')}")
        if row.get("claim_state") not in allowed_states:
            errors.append(f"invalid claim state for {row.get('id')}")
        artifact = row.get("artifact_or_url", "")
        if not artifact:
            errors.append(f"missing source for {row.get('id')}")
        elif not artifact.startswith("https://") and not (ROOT / artifact).exists():
            errors.append(f"missing local evidence artifact for {row.get('id')}: {artifact}")


def main() -> int:
    errors: list[str] = []
    check_required(errors)
    check_text(errors)
    check_markdown_links(errors)
    check_initial_scores(errors)
    check_critical_data_scores(errors)
    check_evidence(errors)

    if errors:
        print("Repository checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

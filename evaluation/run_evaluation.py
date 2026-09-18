"""Run the EgoBiz Wiki evaluation dataset against the production RAG pipeline."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from app.api.dependencies import get_rag_service
from app.application.rag.service import FALLBACK_ANSWER
from app.domain.rag import RAGResponse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "evaluation" / "dataset.yaml"


@dataclass(frozen=True)
class EvaluationCase:
    """Represent one evaluation case."""

    case_id: str
    question: str
    category: str
    expected_behavior: str
    expected_sources: tuple[str, ...]


@dataclass(frozen=True)
class CaseResult:
    """Represent the evaluation result for one case."""

    case: EvaluationCase
    actual_behavior: str
    actual_sources: tuple[str, ...]
    behavior_passed: bool
    source_hit_passed: bool
    source_attribution_passed: bool


@dataclass(frozen=True)
class EvaluationSummary:
    """Represent aggregated evaluation metrics."""

    total_cases: int
    behavior_accuracy: float
    source_hit_rate: float
    source_attribution_accuracy: float
    fallback_accuracy: float
    results: tuple[CaseResult, ...]


def _load_dataset(path: Path) -> list[EvaluationCase]:
    """Load evaluation cases from the YAML dataset."""
    with path.open("r", encoding="utf-8") as file:
        payload: dict[str, Any] = yaml.safe_load(file)

    raw_cases = payload.get("cases", [])
    if not isinstance(raw_cases, list):
        raise ValueError("Evaluation dataset must contain a 'cases' list.")

    cases: list[EvaluationCase] = []

    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            raise ValueError("Each evaluation case must be a mapping.")

        cases.append(
            EvaluationCase(
                case_id=str(raw_case["id"]),
                question=str(raw_case["question"]),
                category=str(raw_case["category"]),
                expected_behavior=str(raw_case["expected_behavior"]),
                expected_sources=tuple(
                    str(source)
                    for source in raw_case.get("expected_sources", [])
                ),
            )
        )

    if not cases:
        raise ValueError("Evaluation dataset is empty.")

    return cases


def _classify_behavior(response: RAGResponse) -> str:
    """Classify the observable behavior of the current RAG contract."""
    answer = response.answer.strip()

    if FALLBACK_ANSWER in answer:
        return "fallback"

    return "answer"


def _source_names(response: RAGResponse) -> tuple[str, ...]:
    """Extract unique document identifiers from a RAG response."""
    return tuple(
        dict.fromkeys(source.document_id for source in response.sources)
    )


def _expected_source_ids(
    expected_sources: tuple[str, ...],
) -> set[str]:
    """Convert dataset source paths to production document identifiers."""
    special_cases = {
        "knowledge_base/customer_operations/customer_communication.md":
            "customer-operations-communication",
        "knowledge_base/faq/general_faq.md":
            "faq-general",
    }

    source_ids: set[str] = set()

    for source in expected_sources:
        if source in special_cases:
            source_ids.add(special_cases[source])
            continue

        path = PurePosixPath(source)

        if not path.parts or path.parts[0] != "knowledge_base":
            raise ValueError(
                f"Expected source must start with 'knowledge_base/': {source}"
            )

        document_parts = [
            part.removesuffix(".md").replace("_", "-")
            for part in path.parts[1:]
        ]

        if not document_parts:
            raise ValueError(f"Invalid expected source path: {source}")

        source_ids.add("-".join(document_parts))

    return source_ids


def _evaluate_case(
    case: EvaluationCase,
    response: RAGResponse,
) -> CaseResult:
    """Evaluate one RAG response against the expected case contract."""
    actual_behavior = _classify_behavior(response)
    actual_sources = _source_names(response)

    behavior_passed = actual_behavior == case.expected_behavior

    expected_source_ids = _expected_source_ids(case.expected_sources)
    actual_source_set = set(actual_sources)

    if expected_source_ids:
        source_hit_passed = bool(
            expected_source_ids & actual_source_set
        )
        source_attribution_passed = (
            expected_source_ids <= actual_source_set
        )
    else:
        source_hit_passed = not actual_source_set
        source_attribution_passed = not actual_source_set

    return CaseResult(
        case=case,
        actual_behavior=actual_behavior,
        actual_sources=actual_sources,
        behavior_passed=behavior_passed,
        source_hit_passed=source_hit_passed,
        source_attribution_passed=source_attribution_passed,
    )


def _percentage(passed: int, total: int) -> float:
    """Calculate a percentage without division by zero."""
    if total == 0:
        return 0.0

    return passed / total * 100


def _calculate_summary(
    cases: list[EvaluationCase],
    results: list[CaseResult],
) -> EvaluationSummary:
    """Calculate aggregate evaluation metrics."""
    total_cases = len(cases)

    behavior_passed = sum(result.behavior_passed for result in results)

    source_cases = [
        result
        for result in results
        if result.case.expected_sources
    ]

    source_hit_passed = sum(
        result.source_hit_passed
        for result in source_cases
    )
    source_attribution_passed = sum(
        result.source_attribution_passed
        for result in source_cases
    )

    fallback_cases = [
        result
        for result in results
        if result.case.expected_behavior == "fallback"
    ]
    fallback_passed = sum(
        result.behavior_passed for result in fallback_cases
    )

    return EvaluationSummary(
        total_cases=total_cases,
        behavior_accuracy=_percentage(
            behavior_passed,
            total_cases,
        ),
        source_hit_rate=_percentage(
            source_hit_passed,
            len(source_cases),
        ),
        source_attribution_accuracy=_percentage(
            source_attribution_passed,
            len(source_cases),
        ),
        fallback_accuracy=_percentage(
            fallback_passed,
            len(fallback_cases),
        ),
        results=tuple(results),
    )


def _print_summary(summary: EvaluationSummary) -> None:
    """Print concise presentation-friendly evaluation results."""
    source_cases = sum(
        bool(result.case.expected_sources)
        for result in summary.results
    )

    print()
    print("=" * 64)
    print("EgoBiz Wiki — Evaluation")
    print("=" * 64)
    print(f"Cases:                         {summary.total_cases}")
    print(f"Source cases:                  {source_cases}")
    print(f"Behavior Accuracy:             {summary.behavior_accuracy:.1f}%")
    print(f"Expected Source Hit Rate:      {summary.source_hit_rate:.1f}%")
    print(
        "Source Attribution Accuracy: "
        f"{summary.source_attribution_accuracy:.1f}%"
    )
    print(f"Fallback Accuracy:             {summary.fallback_accuracy:.1f}%")
    print("=" * 64)

    failed_results = [
        result
        for result in summary.results
        if not (
            result.behavior_passed
            and result.source_hit_passed
            and result.source_attribution_passed
        )
    ]

    if not failed_results:
        print("Failed cases:                  0")
        print()
        return

    print(f"Failed cases:                  {len(failed_results)}")
    print()

    for result in failed_results:
        print(
            f"- {result.case.case_id}: "
            f"expected={result.case.expected_behavior}, "
            f"actual={result.actual_behavior}"
        )

        if result.case.expected_sources:
            expected = ", ".join(result.case.expected_sources)
            actual = ", ".join(result.actual_sources) or "none"
            print(f"  expected sources: {expected}")
            print(f"  actual sources:   {actual}")


def main() -> int:
    """Run the full evaluation dataset."""
    print("Loading evaluation dataset...")
    cases = _load_dataset(DATASET_PATH)

    print(f"Running {len(cases)} cases against the RAG pipeline...")

    rag_service = get_rag_service()
    results: list[CaseResult] = []

    for index, case in enumerate(cases, start=1):
        print(
            f"[{index:02d}/{len(cases):02d}] "
            f"{case.case_id}: {case.question}"
        )

        try:
            response = rag_service.answer(case.question)
        except Exception as exc:
            print(f"  ERROR: {exc}")
            return 1

        results.append(_evaluate_case(case, response))

    summary = _calculate_summary(cases, results)
    _print_summary(summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())

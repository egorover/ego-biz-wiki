"""Tests for the evaluation runner."""

from app.application.rag.service import FALLBACK_ANSWER
from app.domain.rag import RAGResponse, RAGSource
from evaluation.run_evaluation import (
    EvaluationCase,
    _classify_behavior,
    _evaluate_case,
    _expected_source_ids,
)


def _response(
    answer: str,
    sources: list[str],
) -> RAGResponse:
    """Build a test RAG response."""
    return RAGResponse(
        answer=answer,
        sources=[
            RAGSource(
                document_id=source,
                title=f"Document {index}",
                source=source,
            )
            for index, source in enumerate(sources)
        ],
    )


def test_classify_answer() -> None:
    """Classify a normal response as answer."""
    response = _response(
        answer="В компании используется корпоративный VPN.",
        sources=["it-vpn"],
    )

    assert _classify_behavior(response) == "answer"


def test_classify_fallback() -> None:
    """Classify the exact fallback response as fallback."""
    response = _response(
        answer=FALLBACK_ANSWER,
        sources=[],
    )

    assert _classify_behavior(response) == "fallback"


def test_classify_explanatory_fallback() -> None:
    """Classify an explanatory fallback response as fallback."""
    response = _response(
        answer=(
            "В предоставленном контексте нет информации о том, "
            "как оформить отпуск по уходу за ребёнком. "
            f"{FALLBACK_ANSWER}"
        ),
        sources=[],
    )

    assert _classify_behavior(response) == "fallback"


def test_evaluate_expected_source() -> None:
    """Pass when the expected source is retrieved."""
    case = EvaluationCase(
        case_id="test-001",
        question="Как подключиться к VPN?",
        category="relevant",
        expected_behavior="answer",
        expected_sources=("knowledge_base/it/vpn.md",),
    )
    response = _response(
        answer="Используйте корпоративный VPN.",
        sources=["it-vpn"],
    )

    result = _evaluate_case(case, response)

    assert result.behavior_passed is True
    assert result.source_hit_passed is True
    assert result.source_attribution_passed is True


def test_evaluate_multiple_expected_sources() -> None:
    """Require all expected sources for source attribution accuracy."""
    case = EvaluationCase(
        case_id="test-002",
        question="Комплексный вопрос",
        category="cross_category",
        expected_behavior="answer",
        expected_sources=(
            "knowledge_base/hr/remote_work.md",
            "knowledge_base/it/vpn.md",
        ),
    )
    response = _response(
        answer="Ответ.",
        sources=["it-vpn"],
    )

    result = _evaluate_case(case, response)

    assert result.behavior_passed is True
    assert result.source_hit_passed is True
    assert result.source_attribution_passed is False


def test_evaluate_fallback_without_sources() -> None:
    """Pass an out-of-KB case with the exact fallback and no sources."""
    case = EvaluationCase(
        case_id="test-003",
        question="Вопрос вне базы",
        category="out_of_kb",
        expected_behavior="fallback",
        expected_sources=(),
    )
    response = _response(
        answer=FALLBACK_ANSWER,
        sources=[],
    )

    result = _evaluate_case(case, response)

    assert result.behavior_passed is True
    assert result.source_hit_passed is True
    assert result.source_attribution_passed is True


def test_evaluate_unexpected_sources_for_empty_expected_sources() -> None:
    """Fail source checks when sources appear where none are expected."""
    case = EvaluationCase(
        case_id="test-004",
        question="Неоднозначный вопрос",
        category="ambiguous",
        expected_behavior="clarification",
        expected_sources=(),
    )
    response = _response(
        answer="Уточните, к какой системе нужен доступ.",
        sources=["it-access-requests"],
    )

    result = _evaluate_case(case, response)

    assert result.behavior_passed is False
    assert result.source_hit_passed is False
    assert result.source_attribution_passed is False


def test_expected_source_ids_normalize_dataset_paths() -> None:
    """Convert dataset paths to production document identifiers."""
    result = _expected_source_ids(
        (
            "knowledge_base/it/vpn.md",
            "knowledge_base/customer_operations/sla.md",
            "knowledge_base/security/incident_reporting.md",
        )
    )

    assert result == {
        "it-vpn",
        "customer-operations-sla",
        "security-incident-reporting",
    }

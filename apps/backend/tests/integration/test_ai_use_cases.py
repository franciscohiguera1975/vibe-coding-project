import pytest

from app.application.dto.practice_dto import CreatePracticeInput
from app.application.use_cases.ai.generate_hint import GenerateAIHintUseCase
from app.application.use_cases.ai.generate_practice_feedback import (
    GeneratePracticeFeedbackUseCase,
)
from app.application.use_cases.practices.create_practice import CreatePracticeUseCase
from app.application.use_cases.practices.evaluate_practice import EvaluatePracticeUseCase
from app.application.use_cases.practices.publish_practice import PublishPracticeUseCase
from app.application.use_cases.practices.start_practice import StartPracticeUseCase
from app.application.use_cases.practices.submit_practice import SubmitPracticeUseCase
from app.domain.exceptions import NotFoundError
from app.infrastructure.ai.mock_adapter import MockAIAdapter
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.evaluation.rule_based_adapter import RuleBasedEvaluationAdapter


@pytest.fixture
def ai_provider() -> MockAIAdapter:
    return MockAIAdapter()


@pytest.fixture
def published_practice(admin_user):
    create_use_case = CreatePracticeUseCase(SqlAlchemyUnitOfWork)
    practice = create_use_case.execute(
        actor=admin_user,
        data=CreatePracticeInput(
            title="Practica con pista",
            type="software",
            instructions="Resuelva el problema X",
            content={"model": {"variables": {}}},
            evaluation={"strategy": "numeric_match", "checks": []},
        ),
    )
    PublishPracticeUseCase(SqlAlchemyUnitOfWork).execute(actor=admin_user, practice_id=practice.id)
    return practice


def test_generate_hint_returns_text_without_revealing_answer(
    admin_user, published_practice, ai_provider
):
    use_case = GenerateAIHintUseCase(SqlAlchemyUnitOfWork, ai_provider)
    hint = use_case.execute(actor=admin_user, practice_slug=published_practice.slug)
    assert isinstance(hint, str)
    assert len(hint) > 0


def test_generate_hint_raises_for_unknown_practice(admin_user, ai_provider):
    use_case = GenerateAIHintUseCase(SqlAlchemyUnitOfWork, ai_provider)
    with pytest.raises(NotFoundError):
        use_case.execute(actor=admin_user, practice_slug="no-existe")


def test_generate_feedback_includes_evaluation_context(admin_user, published_practice, ai_provider):
    start_use_case = StartPracticeUseCase(SqlAlchemyUnitOfWork)
    attempt = start_use_case.execute(actor=admin_user, practice_slug=published_practice.slug)

    submit_use_case = SubmitPracticeUseCase(SqlAlchemyUnitOfWork)
    submission = submit_use_case.execute(actor=admin_user, attempt_id=attempt.id, payload={})

    evaluate_use_case = EvaluatePracticeUseCase(SqlAlchemyUnitOfWork, RuleBasedEvaluationAdapter())
    evaluate_use_case.execute(actor=admin_user, submission_id=submission.id)

    feedback_use_case = GeneratePracticeFeedbackUseCase(SqlAlchemyUnitOfWork, ai_provider)
    feedback = feedback_use_case.execute(actor=admin_user, submission_id=submission.id)
    assert isinstance(feedback, str)
    assert len(feedback) > 0

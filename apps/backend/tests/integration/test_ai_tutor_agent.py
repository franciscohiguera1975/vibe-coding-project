import pytest
from sqlalchemy import select

from app.application.dto.practice_dto import CreatePracticeInput
from app.application.services.agent import ai_tutor_agent as agent_module
from app.application.services.agent.ai_tutor_agent import AITutorAgent
from app.application.use_cases.practices.create_practice import CreatePracticeUseCase
from app.application.use_cases.practices.evaluate_practice import EvaluatePracticeUseCase
from app.application.use_cases.practices.publish_practice import PublishPracticeUseCase
from app.application.use_cases.practices.start_practice import StartPracticeUseCase
from app.application.use_cases.practices.submit_practice import SubmitPracticeUseCase
from app.domain.entities.ai_session import AISessionStatus, AIToolCallStatus
from app.domain.exceptions import AgentLimitExceededError
from app.infrastructure.ai.mock_adapter import MockAIAdapter
from app.infrastructure.database.models.ai import AISessionModel
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.evaluation.rule_based_adapter import RuleBasedEvaluationAdapter


@pytest.fixture
def software_practice(admin_user):
    create_use_case = CreatePracticeUseCase(SqlAlchemyUnitOfWork)
    practice = create_use_case.execute(
        actor=admin_user,
        data=CreatePracticeInput(
            title="Practica del agente",
            type="software",
            instructions="Resuelva Z",
            content={"model": {}},
            evaluation={"strategy": "numeric_match", "checks": [{"field": "x", "expected": 1}]},
        ),
    )
    PublishPracticeUseCase(SqlAlchemyUnitOfWork).execute(actor=admin_user, practice_id=practice.id)
    return practice


def _get_session(session_id):
    with SqlAlchemyUnitOfWork() as uow:
        return uow.ai_sessions.get_by_id(session_id)


def _get_tool_calls(session_id):
    with SqlAlchemyUnitOfWork() as uow:
        return uow.ai_tool_calls.list_by_session(session_id)


def test_tool_allowlist_matches_the_seven_named_tools():
    assert set(agent_module.TOOL_ALLOWLIST) == {
        "get_practice",
        "get_student_progress",
        "analyze_submission",
        "generate_hint",
        "validate_answer",
        "analyze_image",
        "generate_feedback",
    }


def test_agent_hint_path_calls_expected_tools_and_completes(admin_user, software_practice):
    agent = AITutorAgent(SqlAlchemyUnitOfWork, MockAIAdapter())
    result = agent.run(
        actor=admin_user, practice_slug=software_practice.slug, user_message="no se como empezar"
    )

    assert result.response
    # get_practice, get_student_progress, generate_hint + la sintesis final
    assert result.iterations_used == 4

    session = _get_session(result.session_id)
    assert session.status == AISessionStatus.COMPLETED

    tool_calls = _get_tool_calls(result.session_id)
    tool_names = [tc.tool_name for tc in tool_calls]
    assert tool_names == ["get_practice", "get_student_progress", "generate_hint"]
    assert all(tc.status == AIToolCallStatus.SUCCESS for tc in tool_calls)


def test_agent_trial_answer_path_calls_validate_answer(admin_user, software_practice):
    agent = AITutorAgent(SqlAlchemyUnitOfWork, MockAIAdapter())
    result = agent.run(
        actor=admin_user,
        practice_slug=software_practice.slug,
        user_message="¿esta bien mi respuesta?",
        trial_answer={"x": 1},
    )
    tool_calls = _get_tool_calls(result.session_id)
    tool_names = [tc.tool_name for tc in tool_calls]
    assert "validate_answer" in tool_names
    validate_call = next(tc for tc in tool_calls if tc.tool_name == "validate_answer")
    assert validate_call.result["would_pass"] is True


def test_agent_submission_path_calls_analyze_and_feedback(admin_user, software_practice):
    start = StartPracticeUseCase(SqlAlchemyUnitOfWork).execute(
        actor=admin_user, practice_slug=software_practice.slug
    )
    submission = SubmitPracticeUseCase(SqlAlchemyUnitOfWork).execute(
        actor=admin_user, attempt_id=start.id, payload={"x": 1}
    )
    EvaluatePracticeUseCase(SqlAlchemyUnitOfWork, RuleBasedEvaluationAdapter()).execute(
        actor=admin_user, submission_id=submission.id
    )

    agent = AITutorAgent(SqlAlchemyUnitOfWork, MockAIAdapter())
    result = agent.run(
        actor=admin_user,
        practice_slug=software_practice.slug,
        user_message="explique mi resultado",
        submission_id=str(submission.id),
    )
    tool_calls = _get_tool_calls(result.session_id)
    tool_names = [tc.tool_name for tc in tool_calls]
    assert "analyze_submission" in tool_names
    assert "generate_feedback" in tool_names


def test_agent_stops_at_iteration_limit_and_marks_session_error(admin_user, software_practice):
    agent = AITutorAgent(SqlAlchemyUnitOfWork, MockAIAdapter(), max_iterations=1)
    with pytest.raises(AgentLimitExceededError):
        agent.run(actor=admin_user, practice_slug=software_practice.slug, user_message="hola")

    with SqlAlchemyUnitOfWork() as uow:
        sessions = list(uow._session.scalars(select(AISessionModel)))
        assert len(sessions) == 1
        assert sessions[0].status.value == "error"
        assert sessions[0].iterations_used == 2

        tool_calls = uow.ai_tool_calls.list_by_session(sessions[0].id)
        assert len(tool_calls) == 2  # get_practice (ok) + get_student_progress (denied: limit)
        assert tool_calls[-1].status.value == "denied"

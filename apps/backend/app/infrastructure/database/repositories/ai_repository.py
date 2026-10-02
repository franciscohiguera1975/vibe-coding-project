import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.ai_session import (
    AIMessage,
    AIMessageRole,
    AISession,
    AISessionStatus,
    AIToolCall,
    AIToolCallStatus,
)
from app.infrastructure.database.models.ai import AIMessageModel, AISessionModel, AIToolCallModel


def _session_to_domain(model: AISessionModel) -> AISession:
    return AISession(
        id=model.id,
        user_id=model.user_id,
        started_at=model.started_at,
        practice_id=model.practice_id,
        agent_type=model.agent_type,
        status=AISessionStatus(model.status.value),
        ended_at=model.ended_at,
        iterations_used=model.iterations_used,
        tokens_used=model.tokens_used,
        metadata=dict(model.session_metadata),
    )


def _message_to_domain(model: AIMessageModel) -> AIMessage:
    return AIMessage(
        id=model.id,
        session_id=model.session_id,
        role=AIMessageRole(model.role.value),
        content=model.content,
        sequence=model.sequence,
    )


def _tool_call_to_domain(model: AIToolCallModel) -> AIToolCall:
    return AIToolCall(
        id=model.id,
        session_id=model.session_id,
        iteration_index=model.iteration_index,
        tool_name=model.tool_name,
        status=AIToolCallStatus(model.status.value),
        arguments=dict(model.arguments),
        result=dict(model.result),
        error_message=model.error_message,
    )


class SqlAlchemyAISessionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, session: AISession) -> AISession:
        model = AISessionModel(
            user_id=session.user_id,
            practice_id=session.practice_id,
            agent_type=session.agent_type,
            status=session.status,
            started_at=session.started_at,
            ended_at=session.ended_at,
            iterations_used=session.iterations_used,
            tokens_used=session.tokens_used,
            session_metadata=dict(session.metadata),
        )
        self._session.add(model)
        self._session.flush()
        return _session_to_domain(model)

    def update(self, session: AISession) -> AISession:
        model = self._session.get(AISessionModel, session.id)
        if model is None:
            raise ValueError(f"AISessionModel {session.id} no encontrado")
        model.status = session.status
        model.ended_at = session.ended_at
        model.iterations_used = session.iterations_used
        model.tokens_used = session.tokens_used
        model.session_metadata = dict(session.metadata)
        self._session.flush()
        return _session_to_domain(model)

    def get_by_id(self, session_id: uuid.UUID) -> AISession | None:
        model = self._session.get(AISessionModel, session_id)
        return _session_to_domain(model) if model else None


class SqlAlchemyAIMessageRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, message: AIMessage) -> AIMessage:
        model = AIMessageModel(
            session_id=message.session_id,
            role=message.role,
            content=message.content,
            sequence=message.sequence,
        )
        self._session.add(model)
        self._session.flush()
        return _message_to_domain(model)

    def list_by_session(self, session_id: uuid.UUID) -> list[AIMessage]:
        rows = self._session.scalars(
            select(AIMessageModel)
            .where(AIMessageModel.session_id == session_id)
            .order_by(AIMessageModel.sequence)
        )
        return [_message_to_domain(m) for m in rows]


class SqlAlchemyAIToolCallRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, tool_call: AIToolCall) -> AIToolCall:
        model = AIToolCallModel(
            session_id=tool_call.session_id,
            iteration_index=tool_call.iteration_index,
            tool_name=tool_call.tool_name,
            arguments=dict(tool_call.arguments),
            result=dict(tool_call.result),
            status=tool_call.status,
            error_message=tool_call.error_message,
        )
        self._session.add(model)
        self._session.flush()
        return _tool_call_to_domain(model)

    def list_by_session(self, session_id: uuid.UUID) -> list[AIToolCall]:
        rows = self._session.scalars(
            select(AIToolCallModel)
            .where(AIToolCallModel.session_id == session_id)
            .order_by(AIToolCallModel.iteration_index)
        )
        return [_tool_call_to_domain(m) for m in rows]
